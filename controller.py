from typing import List
import socketserver
import json
import socket
from os.path import join
# from utility.RouteServer import *
from utility.RouteTable import RouteTable
from utility.LSGraph import LSGraph


def generate_response(**kwargs) -> bytes:
    b = json.dumps(kwargs, ensure_ascii=False) + "\n"
    # return f"{len(b):08X}{b}".encode("UTF-8")
    return b.encode("UTF-8")


def send_message(data: bytes, ip: str, port: int) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    if data[-1] != b'\n':
        data += b'\n'
    s.sendall(data)
    rc = str(s.recv(1024), 'UTF-8')
    # s.shutdown(socket.SHUT_RDWR)
    s.close()
    return rc


class RouteRequestHandler(socketserver.StreamRequestHandler):
    """
     * function need to implement:
     * update_route(dict) -> bool
     * is_destination(str, int) -> bool
     * get_next_hop(str, int) -> Tuple[str, int]
     * get_next_hop_from_controller(dict) -> dict
     * send_route() -> None
    """
    def handle(self):
        while True:
            try:
                parsed_json = {}
                raw_data = ""
                raw_data = self.rfile.readline().decode("UTF-8")
                if raw_data == "" or raw_data == "\n":
                    continue
                parsed_json = json.loads(raw_data)
            except KeyboardInterrupt:
                print("Route Server Prepare to Shutdown!")
                exit(0)
            except Exception:
                print("Route Server Receive Data Error!")
                print(f"raw_data={raw_data}")
                print(f"parsed_json={parsed_json}")
                self.wfile.write(generate_response(code=400))
                continue
            print("Parsed to JSON success!")
            if parsed_json["type"] == "update_route":
                updated = update_route(parsed_json)
                self.wfile.write(generate_response(code=200))
                if updated:
                    send_route()
                print(f"UPDATE_ROUTE from {parsed_json['src_ip']}:{parsed_json['src_port']}")
            elif parsed_json["type"] == "message":
                if is_destination(parsed_json["dst_ip"], parsed_json["dst_port"]):
                    print("RECV:", parsed_json["data"])
                    self.wfile.write(generate_response(code=200))
                else:
                    ip, port = get_next_hop(parsed_json["dst_ip"], parsed_json["dst_port"])
                    send_message(json.dumps(parsed_json, ensure_ascii=False).encode("UTF-8"), ip, port)
                    print("NEXT_HOP:", ip, port)
                    self.wfile.write(generate_response(code=200))
            elif parsed_json["type"] == "get_next_hop":
                print("Get_next_hop:")
                print(parsed_json)
                ip, port = parsed_json["src_ip"], parsed_json["src_port"]
                rd = get_next_hop_from_controller(parsed_json)
                self.wfile.write(json.dumps(rd, ensure_ascii=False).encode("UTF-8"))
                # send_message(json.dumps(rd, ensure_ascii=False).encode("UTF-8"), ip, port)
                print(f"SEND_ROUTE to {ip}:{port}.")


CONTROLLER_IP = "127.0.0.1"
CONTROLLER_PORT = 9006
ROUTERS = ["A", "B", "C", "D", "E", "F"]
ROUTER_IP = "127.0.0.1"
ROUTER_PORTS = [9000, 9001, 9002, 9003, 9004, 9005]


def update_route(data: dict) -> bool:
    # return dvt.update_table_by_table(data["src_ip"], data["src_port"], data["data"])
    return False


def is_destination(ip: str, port: int) -> bool:
    # if ip == CONTROLLER_IP and port == CONTROLLER_PORT:
    #     return True
    return False


def get_next_hop(dst_ip: str, dst_port: int) -> List:
    # return rt.find_next(dst_ip, dst_port)
    return []


def get_next_hop_from_controller(pj: dict) -> dict:
    sip, sport = pj["src_ip"], pj["src_port"]
    for i in range(6):
        j = lsts[i]
        if j.ip == sip and j.port == sport:
            return {"code": 200, "data": rts[i].find_next(pj["dst_ip"], pj["dst_port"])}
    return {"code": 400}


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("Usage:")
    # else len(sys.argv) == 2:
    rts = []
    lsts = []
    for i in range(6):
        rt = RouteTable()
        lst = LSGraph(join(".", "utility", "config", "LSGraph.json"), join(".", "utility", "config", "Mapping.json"),
                      rt, ROUTER_IP, ROUTER_PORTS[i])
        lst.update_route_table(ROUTER_IP, ROUTER_PORTS[i])
        rts.append(rt)
        lsts.append(lst)
    ss = socketserver.ThreadingTCPServer((CONTROLLER_IP, CONTROLLER_PORT), RouteRequestHandler)
    print("PREPARE to start controller...")
    ss.serve_forever()
