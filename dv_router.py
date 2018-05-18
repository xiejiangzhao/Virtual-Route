import logging
# import coloredlogs
import socketserver
import socket
import json
import threading
from time import sleep
from utility.RouteTable import RouteTable
from utility.DVTable import DVTable
from os import path

# coloredlogs.install()
logging.basicConfig(format='[%(asctime)s %(name)s %(levelname)s]:\n%(message)s\n')


# formatter = logging.Formatter('[%(asctime)s %(name)s %(ip)s:%(port)d %(levelname)s]:\n%(message)s\n')
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(formatter)


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


def send_dict_and_recv_bytes(ip: str, port: int, **kwargs):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        send_bytes(s, json.dumps(kwargs, ensure_ascii=False).encode("UTF-8"))
        return recv_bytes(s)


class DVRouteRequestHandler(socketserver.StreamRequestHandler):
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
            self.logger.info(f"Receive heart ping from {sip}:{sport}")
            send_dict(sk, code=200)
        elif parsed_json["type"] == "message":
            pass
        elif parsed_json["type"] == "update_route":
            dvt.update_table_by_table(sip, sport, parsed_json["data"])
            send_dict(sk, code=200)
            if dvt.changed:
                pass
        sk.close()


ROUTERS = ["A", "B", "C", "D", "E", "F"]
ROUTER_IP = "127.0.0.1"
ROUTER_PORTS = [9000, 9001, 9002, 9003, 9004, 9005]

self_ip = ""
self_port = 0
rt: RouteTable = None
dvt: DVTable = None


def start_server(ip: str, port: int) -> None:
    ss = socketserver.ThreadingTCPServer((ip, port), DVRouteRequestHandler)
    logger = logging.getLogger(__name__)
    logger.info(f"Prepare to start RouteServer({ip}:{port})...")
    try:
        ss.serve_forever()
    except KeyboardInterrupt:
        logger.info(f"Prepare to stop RouteServer({ip}:{port})...")
        exit(0)


def heart_loop(rt: RouteTable, dvt: DVTable) -> None:
    while True:
        for i in rt.get_neibour():
            pass


if __name__ == "__main__":
    cid = int(input(f"Please input the client ID(0-{len(ROUTER_PORTS) - 1}):\n"))
    self_ip = ROUTER_IP
    self_port = ROUTER_PORTS[cid]
    rt = RouteTable(path.join(".", "utility", "config", f"{ROUTERS[cid]}route.json"))
    dvt = DVTable(path.join(".", "utility", "config", f"{ROUTERS[cid]}DV.json"), rt, self_ip, self_port)
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
        dip = ROUTER_IP
        dport = ROUTER_PORTS[did]
