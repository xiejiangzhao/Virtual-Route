import socketserver
import json
import socket


def generate_response(**kwargs) -> bytes:
    b = json.dumps(kwargs, ensure_ascii=False) + "\n"
    # return f"{len(b):08X}{b}".encode("UTF-8")
    return b.encode("UTF-8")


def send_message(data: bytes, ip: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall(data)
        rc = str(s.recv(1024), 'UTF-8')
        print(rc)


class RouteRequestHandler(socketserver.StreamRequestHandler):
    """
     * function need to implement:
     * update_route(dict) -> None
     * is_destination(str, int) -> bool
     * get_next_hop(str, int) -> Tuple[str, int]
     * get_route(str, int) -> dict
    """
    def handle(self):
        while True:
            try:
                raw_data = self.rfile.readline().decode("UTF-8")
                if raw_data == "":
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
            if parsed_json["type"] == "update_route":
                update_route(parsed_json["data"])
                self.wfile.write(generate_response(code=200))
                print(f"UPDATE_ROUTE from {parsed_json['src_ip']}:{parsed_json['src_port']}")
            elif parsed_json["type"] == "message":
                if is_destination(parsed_json["dst_ip"], parsed_json["dst_port"]):
                    print("RECV:", parsed_json["data"])
                else:
                    ip, port = get_next_hop(parsed_json["dst_ip"], parsed_json["dst_port"])
                    send_message(json.dumps(parsed_json, ensure_ascii=False).encode("UTF-8"), ip, port)
                    print("NEXT_HOP:", ip, port)
            elif parsed_json["type"] == "get_route_from_controller":
                ip, port = parsed_json["data"]
                rd = get_route(ip, port)
                send_message(json.dumps(rd, ensure_ascii=False).encode("UTF-8"), ip, port)
                print(f"SEND_ROUTE to {ip}:{port}.")
