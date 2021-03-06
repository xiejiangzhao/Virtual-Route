import logging
import socketserver
import socket
import json
import threading
from utility.RouteTable import RouteTable
from utility.LSGraph import LSGraph
from os import path

logging.basicConfig(format='[%(asctime)s %(name)s %(levelname)s]:\n%(message)s\n', level=logging.INFO)


def send_bytes(s: socket.socket, data: bytes) -> None:
    l = len(data)
    ln = f"{l:08X}".encode()
    s.sendall(ln + data)


def recv_bytes(s: socket.socket) -> bytes:
    l = s.recv(8)
    while len(l) < 8:
        l += s.recv(8 - len(l))
    l = int(l, 16)
    data = s.recv(l)
    while len(data) < l:
        data += s.recv(l - len(data))
    return data


def send_dict(s: socket.socket, **kwargs) -> None:
    return send_bytes(s, json.dumps(kwargs, ensure_ascii=False).encode("UTF-8"))


def send_bytes_and_recv_bytes(ip: str, port: int, data: bytes):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        send_bytes(s, data)
        return recv_bytes(s)


def send_dict_and_recv_bytes(ip: str, port: int, **kwargs):
    return send_bytes_and_recv_bytes(ip, port, json.dumps(kwargs, ensure_ascii=False).encode("UTF-8"))


class LSRouteRequestHandler(socketserver.StreamRequestHandler):
    logger = logging.getLogger("RouteServer")

    def handle(self):
        sk = self.request
        raw_data = recv_bytes(sk)
        try:
            parsed_json = json.loads(raw_data, encoding="UTF-8")
        except Exception as e:
            sip, sport = sk.getpeername()
            self.logger.error(f"Parsed to json error.\nFrom {sip}:{sport}\nraw_data={raw_data}\n{e}")
            return
        sip, sport = parsed_json["src_ip"], parsed_json["src_port"]
        dip, dport = parsed_json["dst_ip"], parsed_json["dst_port"]
        if parsed_json["type"] == "heart":
            self.logger.debug(f"Receive heart ping from {sip}:{sport}")
            send_dict(sk, code=200)
        elif parsed_json["type"] == "message":
            if dip == self_ip and dport == self_port:
                self.logger.info(f"Receive message from {sip}:{sport} :\n{parsed_json['data']}")
                send_dict(sk, code=200)
            else:
                nip, nport = rt.find_next(dip, dport)
                send_dict(sk, code=200)
                rd = send_bytes_and_recv_bytes(nip, nport, raw_data)
                self.logger.info(f"Transport message to next hop {nip}:{nport}.\nResponse: {rd}")
        sk.close()


ROUTERS = ["A", "B", "C", "D", "E", "F"]
ROUTER_IP = "127.0.0.1"
ROUTER_PORTS = [9000, 9001, 9002, 9003, 9004, 9005]

self_ip = ""
self_port = 0
rt: RouteTable = None
dvt: LSGraph = None
first_broadcast: bool = True


def start_server(ip: str, port: int) -> None:
    ss = socketserver.ThreadingTCPServer((ip, port), LSRouteRequestHandler)
    logger = logging.getLogger("main")
    # logger.setLevel(logging.INFO)
    logger.info(f"Prepare to start RouteServer({ip}:{port})...")
    try:
        ss.serve_forever()
    except KeyboardInterrupt:
        logger.info(f"Prepare to stop RouteServer({ip}:{port})...")
        exit(0)


if __name__ == "__main__":
    cid = int(input(f"Please input the client ID(0-{len(ROUTER_PORTS) - 1}):\n"))
    self_ip = ROUTER_IP
    self_port = ROUTER_PORTS[cid]
    rt = RouteTable()
    dvt = LSGraph(path.join(".", "utility", "config", f"LSGraph.json"),
                  path.join(".", "utility", "config", "Mapping.json"), rt, self_ip, self_port)
    dvt.update_route_table(self_ip, self_port)
    server_thread = threading.Thread(target=start_server, args=(self_ip, self_port))
    server_thread.start()
    hm = ""
    while True:
        if hm == "y" or hm == "n":
            break
        hm = input("Would you like to send message? y/n ")
    if hm == "y":
        ms = input("Please input your message:\n")
        did = int(input(f"Please input destination ID(0-{len(ROUTER_PORTS) - 1}):\n"))
        dstip = ROUTER_IP
        dstport = ROUTER_PORTS[did]
        hip, hport = rt.find_next(dstip, dstport)
        cnt = 10000
        while cnt > 0:
            cnt -= 1
        rcd = send_dict_and_recv_bytes(hip, hport, type="message", src_ip=self_ip, src_port=self_port, dst_ip=dstip,
                                       dst_port=dstport, data=ms)
        logging.info(f"Send message to {dstip}:{dstport} and receive:\n{rcd}")
    logging.info("Prepare to enter shell...")
    while True:
        hm = input(f"Route{ROUTERS[cid]}> ")
        if hm.lower() == "exit":
            exit(0)
        elif hm.lower() == "show route":
            rt.print_table()
