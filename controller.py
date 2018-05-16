import sys
import socketserver
from typing import List
from os.path import join
from utility.RouteServer import *
from utility.RouteTable import RouteTable
from utility.LSGraph import LSGraph

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
    sip, sport = pj["data"]
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
    s = socketserver.ThreadingTCPServer((CONTROLLER_IP, CONTROLLER_PORT), RouteRequestHandler)
    print("PREPARE to start controller...")
    s.serve_forever()
