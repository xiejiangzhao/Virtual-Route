import socketserver
import json


def generateResponse(**kwargs) -> bytes:
    b = json.dumps(kwargs, ensure_ascii=False) + "\n"
    return f"{len(b):08}{b}".encode("UTF-8")



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
                self.wfile.write(generateResponse(code=400))
