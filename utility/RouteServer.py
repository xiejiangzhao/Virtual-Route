import socketserver
import json


def generate_response(**kwargs) -> bytes:
    b = json.dumps(kwargs, ensure_ascii=False) + "\n"
    return f"{len(b):08X}{b}".encode("UTF-8")


class RouteServer(socketserver.ThreadingTCPServer):
    def __init__(self, server_address, RequestHandlerClass, route_table):
        super().__init__(server_address, RequestHandlerClass)
        self.route_table = route_table


class RouteRequestHandler(socketserver.StreamRequestHandler):
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
            elif parsed_json["type"] == "message":
                pass
