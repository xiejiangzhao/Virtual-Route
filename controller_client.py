import json
import socketserver
import threading

from utility.RouteServer import generate_response, send_message

CONTROLLER_IP = "127.0.0.1"
CONTROLLER_PORT = 9006
ROUTERS = ["A", "B", "C", "D", "E", "F"]
ROUTER_IP = "127.0.0.1"
ROUTER_PORTS = [9000, 9001, 9002, 9003, 9004, 9005]
self_ip = ""
self_port = 0


class ClientRequestHandler(socketserver.StreamRequestHandler):
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
                print(f"raw_data_hex={raw_data.encode('UTF-8')}")
                print(f"parsed_json={parsed_json}")
                self.wfile.write(generate_response(code=400))
                continue
            print("Parsed to JSON success!")
            if parsed_json["type"] == "message":
                self.wfile.write(generate_response(code=200))
                if parsed_json["dst_ip"] == self_ip and parsed_json["dst_port"] == self_port:
                    print(f"RECV: {parsed_json['data']}\nfrom {parsed_json['src_ip']}:{parsed_json['src_port']}")
                    self.wfile.write(generate_response(code=200))
                else:
                    dip, dport = parsed_json["dst_ip"], parsed_json["dst_port"]
                    rd = send_message(generate_response(type="get_next_hop", src_ip=self_ip, src_port=self_port, dst_ip=dip, dst_port=dport), CONTROLLER_IP, CONTROLLER_PORT)
                    print("SEND.")
                    print(rd)
                    print(self_ip, self_port)
                    pj = json.loads(rd)
                    if pj["code"] == 200:
                        print(f"Prepare to send message to {pj['data'][0]}:{pj['data'][1]}")
                        nip, nport = pj["data"]
                        rc = send_message(json.dumps(parsed_json, ensure_ascii=False).encode("UTF-8"), nip, nport)
                        print(f"TRANS: {rc}")
                        self.wfile.write(generate_response(code=200))
                    else:
                        print(f"ERROR: {pj}")
                        self.wfile.write(generate_response(code=400))
            else:
                print(f"ERROR: {parsed_json}")
            break


def start_server(ip: str, port: int, handler) -> None:
    ss = socketserver.ThreadingTCPServer((ip, port), handler)
    print("PREPARE to start controller...")
    ss.serve_forever()


if __name__ == "__main__":
    cid = int(input(f"Please input the client ID(0-{len(ROUTER_PORTS) - 1}):\n"))
    self_ip = ROUTER_IP
    self_port = ROUTER_PORTS[cid]
    # new_thread = threading.Thread(target=start_server, args=(conn_thread, addr))
    # new_thread.start()
    hm = ""
    while True:
        if hm == "y" or hm == "n":
            break
        hm = input("Would you like to send message? y/n ")
    if hm == "y":
        ms = input("Please input your message:\n")
        dip = input("Please input destination ip:\n")
        dport = int(input("Please input destination port:\n"))
        rd = send_message(generate_response(type="get_next_hop", src_ip=ROUTER_IP, src_port=ROUTER_PORTS[cid], dst_ip=dip, dst_port=dport), CONTROLLER_IP, CONTROLLER_PORT)
        print(rd)
        pj = json.loads(rd)
        if pj["code"] == 200:
            nip, nport = pj["data"]
            rc = send_message(generate_response(type="message", src_ip=ROUTER_IP, src_port=ROUTER_PORTS[cid], dst_ip=dip, dst_port=dport, data=ms), nip, nport)
            print(f"TRANS: {rc}")
        else:
            print(f"ERROR: {pj}")
    ss = socketserver.ThreadingTCPServer((ROUTER_IP, ROUTER_PORTS[cid]), ClientRequestHandler)
    print("PREPARE to start controller...")
    ss.serve_forever()
