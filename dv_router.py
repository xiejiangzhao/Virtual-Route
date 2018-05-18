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
logging.basicConfig(format='[%(asctime)s %(name)s %(levelname)s]:\n%(message)s\n', level=logging.INFO)


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


def send_bytes_and_recv_bytes(ip: str, port: int, data: bytes):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        send_bytes(s, data)
        return recv_bytes(s)


def send_dict_and_recv_bytes(ip: str, port: int, **kwargs):
    return send_bytes_and_recv_bytes(ip, port, json.dumps(kwargs, ensure_ascii=False).encode("UTF-8"))


class DVRouteRequestHandler(socketserver.StreamRequestHandler):
    logger = logging.getLogger("RouteServer")
    # initial_level = True

    def handle(self):
        # if self.initial_level:
            # self.initial_level = False
            # self.logger.setLevel(logging.INFO)
        # global rt, dvt
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
        elif parsed_json["type"] == "update_route":
            dvt.update_table_by_table(sip, sport, parsed_json["data"])
            send_dict(sk, code=200)
            if dvt.changed:
                dvt.reset_change()
                for i in rt.get_neibour():
                    if sip == i[0] and sport == i[1]:
                        continue
                    rd = send_dict_and_recv_bytes(i[0], i[1], type="update_route", src_ip=self_ip, src_port=self_port,
                                                  dst_ip=i[0], dst_port=i[1], data=dvt.DVTable)
                    self.logger.debug(f"Send route table to {i[0]}:{i[1]} and receive:\n{rd}")
        sk.close()


ROUTERS = ["A", "B", "C", "D", "E", "F"]
ROUTER_IP = "127.0.0.1"
ROUTER_PORTS = [9000, 9001, 9002, 9003, 9004, 9005]

self_ip = ""
self_port = 0
rt: RouteTable = None
dvt: DVTable = None
first_broadcast: bool = True


def start_server(ip: str, port: int) -> None:
    ss = socketserver.ThreadingTCPServer((ip, port), DVRouteRequestHandler)
    logger = logging.getLogger("main")
    # logger.setLevel(logging.INFO)
    logger.info(f"Prepare to start RouteServer({ip}:{port})...")
    try:
        ss.serve_forever()
    except KeyboardInterrupt:
        logger.info(f"Prepare to stop RouteServer({ip}:{port})...")
        exit(0)


def heart_loop(rt: RouteTable, dvt: DVTable) -> None:
    logger = logging.getLogger("HeartLoop")
    # logger.setLevel(logging.INFO)
    # global first_broadcast, self_ip, self_port
    first_broadcast: bool = True
    while True:
        if first_broadcast:
            first_broadcast = False
            for i in rt.get_neibour():
                rd = send_dict_and_recv_bytes(i[0], i[1], type="update_route", src_ip=self_ip, src_port=self_port,
                                              dst_ip=i[0], dst_port=i[1], data=dvt.DVTable)
                logger.debug(f"Send route table to {i[0]}:{i[1]} and receive:\n{rd}")
        else:
            sleep(10)
            for i in rt.get_all_member():
                sleep(1)
                try:
                    rd = send_dict_and_recv_bytes(i[0], i[1], type="heart", src_ip=self_ip, src_port=self_port,
                                                  dst_ip=i[0], dst_port=i[1])
                    logger.info(f"Router {i[0]}:{i[1]} online.")
                except ConnectionError:
                    dvt.route_offline(i[0], i[1])
                    logger.error(f"Router {i[0]}:{i[1]} offline!")
                    dvt.reset_change()
                    for j in rt.get_neibour():
                        rd = send_dict_and_recv_bytes(j[0], j[1], type="update_route", src_ip=self_ip,
                                                      src_port=self_port, dst_ip=j[0], dst_port=j[1], data=dvt.DVTable)
                        logger.debug(f"Send route table to {j[0]}:{j[1]} and receive:\n{rd}")


if __name__ == "__main__":
    cid = int(input(f"Please input the client ID(0-{len(ROUTER_PORTS) - 1}):\n"))
    self_ip = ROUTER_IP
    self_port = ROUTER_PORTS[cid]
    rt = RouteTable(path.join(".", "utility", "config", f"{ROUTERS[cid]}route.json"))
    dvt = DVTable(path.join(".", "utility", "config", f"{ROUTERS[cid]}DV.json"), rt, self_ip, self_port)
    server_thread = threading.Thread(target=start_server, args=(self_ip, self_port))
    server_thread.start()
    sleep(1)
    heart_thread = threading.Thread(target=heart_loop, args=(rt, dvt))
    heart_thread.start()
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
        sleep(3)
        hip, hport = rt.find_next(dstip, dstport)
        rcd = send_dict_and_recv_bytes(nip, nport, type="message", src_ip=self_ip, src_port=self_port, dst_ip=dstip,
                                       dst_port=dstport, data=ms)
        logging.info(f"Send message to {dstip}:{dstport} and receive:\n{rcd}")
    logging.info("Prepare to enter shell...")
    while True:
        hm = input(f"Route{ROUTERS[cid]}> ")
        if hm.lower() == "exit":
            exit(0)
        elif hm.lower() == "show route":
            rt.print_table()
        elif hm.lower() == "show dv":
            dvt.print_table()
