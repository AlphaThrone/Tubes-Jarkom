import socket
import sys
from lib.Segment import Segment
from lib.FileWriter import FileWriter

class Client:
    def __init__(self, server_address: str, server_port: int, client_address: str, client_port: int):
        self.server_address = (server_address, server_port)
        self.client_address = (client_address, client_port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind(self.client_address)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.req_num = 0
        self.ack_num = 0
        self.running = True
        
    def response(self, frames: list[bytes], chunk: Segment, data: list[bytes]):
        # 
        if (not int.from_bytes(data[:4], 'little') == self.req_num):
            print(f"[!] Denied segment {int.from_bytes(data[:4], 'little')}")
        # if segment checksum is invalid
        elif (not chunk.is_valid_checksum()):
            print(f"[!] Corrupted! Segment {self.req_num}")
            print(f"[!] Request resend: Segment {self.req_num}")
            invalid_req = self.req_num - 1
            invalid_ack = self.ack_num
            self.client_socket.sendto(Segment.ack(invalid_req, invalid_ack).get_segment_bytes(), self.server_address)
        # segment is all valid
        else:
            print(f'[!] ACK: {int.from_bytes(data[4:8], "little")}')
            print(f'[!] Segment {int.from_bytes(data[:4], "little")} ({len(data[12:])} bytes) received')
            frames.insert(self.ack_num,data[12:])
            self.ack_num = self.req_num
            self.req_num += 1
            self.client_socket.sendto(Segment.ack(self.req_num, self.ack_num).get_segment_bytes(), self.server_address)
        
    def start(self):
        while True:
            try:
                frames = list[bytes]()
                print(f'[!] Requesting connection...')
                print(f'[!] SYN')
                self.client_socket.sendto(Segment.syn(self.req_num).get_segment_bytes(), self.server_address)
                while self.running:
                    try:
                        self.client_socket.settimeout(1)
                        data, addr = self.client_socket.recvfrom(32768)
                        chunk = Segment(flags=data[8:9], 
                                            seq_num=data[:4],
                                            ack_num=data[4:8],
                                            checksum=data[10:12],
                                            payload=data[12:])
                        flags = data[8:9]
                        
                        # segment flag is syn ack
                        if (flags == 0b1010.to_bytes()):
                            
                            print(f'[!] Connection accepted by {addr[0]}:{addr[1]}')
                            self.ack_num = self.req_num
                            self.req_num += 1
                            self.response(frames, chunk, data)
                        
                        # segment flag is not syn nor ack (sending payload segment)
                        elif (flags == 0b0000.to_bytes() and data[12:] not in frames):
                            self.response(frames, chunk, data)
                        elif (flags == 0b0001.to_bytes() and data[12:] not in frames):
                            print("[!] All Frames Acquired...")
                            print("[!] Compiling file...")
                            write = FileWriter(frames, data[12:].decode())
                            write.write_file()
                            print("[!] FIN ACK")
                            self.client_socket.sendto(Segment.fin_ack().get_segment_bytes(), self.server_address)
                            self.close()
                        else:
                            continue
                    except socket.timeout:
                        print("[!] Connection timed out")
                        print(f'[!] Resend ACK: {int.from_bytes(data[:4], "little")}')
                        self.ack_num = self.req_num-1
                        if (self.ack_num < 0):
                            self.ack_num = 0
                        self.client_socket.sendto(Segment.ack(self.req_num, self.ack_num).get_segment_bytes(), self.server_address)
                    except UnicodeDecodeError:
                        print('[!] Decoding fault')
                        print('[!] Retrying')
                    except socket.error:
                        print("[!] Closing...")
                        self.running = False
                        self.close()
                break
            except UnboundLocalError:
                print("[!] Error: Resolving")
                self.ack_num = self.req_num
                
                
                    

    def send_message(self, message: str):
        self.client_socket.sendto(message.encode(), self.server_address)
        print(f"Message sent to {self.server_address}: {message}")
        
    def stop_server(self):
        stop_message = "stop_server"
        self.client_socket.sendto(stop_message.encode(), self.server_address)

    def close(self):
        self.client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("CLI: python Client.py [client port] [broadcast port]")
        sys.exit(1)

    try:
        client_port = int(sys.argv[1])
        server_port = int(sys.argv[2])
    except ValueError:
        print("Error: Invalid port number")
        sys.exit(1)
    server_address = '<broadcast>'
    client_address = '127.23.21.2'
    client = Client(server_address, server_port, client_address, client_port)
    client.start()