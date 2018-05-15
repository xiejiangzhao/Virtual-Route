import sys
from typing import List
from utility.RouteServer import *
from utility.RouteTable import RouteTable
from utility.DVTable import DVTable


CONTROLLER_IP = '127.0.0.1'
CONTROLLER_PORT = 9006


def update_route(data: dict) -> bool:
    return dvt.update_table_by_table(data["src_ip"], data["src_port"], data["data"])
def is_destination(ip: str, port: int) -> bool:
    if ip == CONTROLLER_IP and port == CONTROLLER_PORT:
        return True
    return False
def get_next_hop(dst_ip: str, dst_port: int) -> List:
    return rt.find_next(dst_ip, dst_port)
def get_route(ip: str, port: int) -> dict:
    pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
    elif len(sys.argv) == 3:
        rt = RouteTable(sys.argv[1])
        dvt = DVTable(sys.argv[2], rt)
