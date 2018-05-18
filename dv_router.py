import logging
import coloredlogs
import socketserver
import socket
import json


coloredlogs.install()
logging.basicConfig(format='[%(asctime)s - %(name)s - %(levelname)s - %(ip)s:%(port)d] : \n%(message)s\n')



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


class DVRouteRequestHandler(socketserver.StreamRequestHandler):
    logger = logging.getLogger("RouteServer")

    def handle(self):
        sk = self.request
        raw_data = recv_bytes(sk)
        try:
            parsed_json = json.loads(raw_data, encoding="UTF-8")
        except Exception as e:
            logger.error(f"Parsed to json error.\nraw_data={raw_data}\n{e}")
            return
        if parsed_json["type"] == "heart":
            send_dict(sk, code=200)
        elif parsed_json["type"] == "message":
            pass
        elif parsed_json["type"] == "update_route":
            pass
        sk.close()


ROUTERS = ["A", "B", "C", "D", "E", "F"]
ROUTER_IP = "127.0.0.1"
ROUTER_PORTS = [9000, 9001, 9002, 9003, 9004, 9005]

self_ip = ""
self_port = 0

if __name__ == "__main__":
    cid = int(input(f"Please input the client ID(0-{len(ROUTER_PORTS) - 1}):\n"))
    self_ip = ROUTER_IP
    self_port = ROUTER_PORTS[cid]
    hm = ""
    while True:
        if hm == "y" or hm == "n":
            break
        hm = input("Would you like to send message? y/n ")
    if hm == "y":
        ms = input("Please input your message:\n")
        dip = input("Please input destination ip:\n")
        dport = int(input("Please input destination port:\n"))
