import socket
import sys
from lib.FileParser import FileParser
from lib.Segment import Segment

class Server:
    def __init__(self, host: str, port: int, file_path: str):
        self.host = host
        self.port = port
        self.file_path = file_path
        names = file_path.split('\\')
        names = names[len(names)-1].split('/')
        self.file_name = 'sent-'+names[len(names)-1]
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server_socket.bind((self.host, self.port))
        self.running = True
        
    def send_frames(self, seq_num: int, req_num: int, client_address: [str,int], frames: list[bytes], acks: list[int]) -> None:
        try:
            print(f"[!] Sending segment {seq_num}")
            segment = Segment(seq_num=seq_num, ack_num=req_num, payload=frames[seq_num-1])
            segment.update_checksum()
            self.server_socket.sendto(segment.get_segment_bytes(), client_address)
        except:
            print("[!] Out of range")

    def start(self):
        acks = list[int]()
        isrun = False
        win_size = 3
        req_num = int()
        seq_num = 0
        seq_base = 0
        gap = 0
        seq_max = win_size + 1
        
        print(f'[!] File name will be: {self.file_name}')
        print(f"[!] Server listening on {self.host}:{self.port}")
        client_list = list[int]()
        file = FileParser(self.file_path)
        frames = file.create_segments()
        while self.running:
            try:
                data, client_address = self.server_socket.recvfrom(32768)
                self.server_socket.settimeout(1)
                flags = data[8:9]
                if client_address[1] not in client_list and flags==0b0010.to_bytes():
                    print(f"[!] Received request from {client_address}")
                    #syn_ack
                    print(f"[!] SYN ACK")
                    self.server_socket.sendto(Segment.syn_ack().get_segment_bytes(), client_address)
                    #listing address
                    client_list.append(client_address[1])
                    print(f"[!] Accepted connection from {client_address}")
                    listen = True
                    while listen:
                        confirm = input("[?] Listen more (y)?: ")
                        if (confirm.lower() != 'y'):
                            break
                        data, client_address = self.server_socket.recvfrom(32768)
                        flags = data[8:9]
                        print(f"[!] Received request from {client_address}")
                        self.server_socket.sendto(Segment.syn_ack().get_segment_bytes(), client_address)
                        client_list.append(client_address[1])
                        print(f"[!] Accepted connection from {client_address}")
                        data, client_address = self.server_socket.recvfrom(32768) 
                elif flags==0b1000.to_bytes():
                    req_num = int.from_bytes(data[4:8], byteorder='little')
                    acks.append(req_num)
                    print(f"[!] Received ack {req_num} from {client_address}")
                    seq_num = int.from_bytes(data[:4], byteorder='little')
                    print(f'[!] Seq num: {seq_num}')
                    if (seq_num > seq_base):
                        seq_max = (seq_max - seq_base) + seq_num
                        seq_base = seq_num
                    if (isrun):
                        gap = seq_max - seq_num
                        if (gap > win_size + 1):
                            gap = 1
                    else:
                        gap = 1
                    while (seq_base <= seq_num+gap <= seq_max and seq_num):
                        if (acks[len(acks)-1] < len(frames) and seq_num + gap not in acks):
                            self.send_frames(seq_num, req_num, client_address, frames, acks)
                        elif (acks[len(acks)-1] == len(frames)):
                            isrun = False
                            print(f"[!] FIN")
                            self.server_socket.sendto(Segment.fin(self.file_name).get_segment_bytes(), client_address)
                            break
                        seq_num += 1
                    isrun = True
                    # print(f'Gap: {gap}')
                elif flags==0b1001.to_bytes():
                    self.server_socket.detach()
                
            except socket.timeout:
                print("[!] Timeout!")
                gap = 1
                isrun = False
                if (seq_num == len(frames)+1):
                    print(f"[!] FIN")
                    self.server_socket.sendto(Segment.fin(self.file_name).get_segment_bytes(), client_address)
                else:
                    self.send_frames(seq_num, req_num, client_address, frames, acks)
            except socket.error:
                print(f'[!] Original file hash: {file.get_file_hash()}')
                print("[!] Server out")
                self.running = False
                

    def close(self):
        self.server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("[!] python Server.py [broadcast port] [path file input]")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        print("[!] Error: Invalid port number")
        sys.exit(1)
    file_path = sys.argv[2]
    #buat process file
    server_host = '0.0.0.0'
    server_port = port

    server = Server(server_host, server_port, file_path)
    server.start()
