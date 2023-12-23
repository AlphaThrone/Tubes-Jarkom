import hashlib

class FileParser:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.file_hash = ""
        
    def create_segments(self) -> list[bytes]:
        with open(self.file_path, 'rb') as file:
            file_bytes = file.read()
        max_payload = 32756
        frame_payloads = [file_bytes[i:i + max_payload]
                       for i in range(0, len(file_bytes), max_payload)]
        # for i, chunk in enumerate(frame_payloads):
        #     print(f"Frame {i + 1}: Size = {len(chunk)} bytes")
        self.file_hash = hashlib.md5(file_bytes).hexdigest()
        print(f'[!] Original file hash: {self.file_hash}')
        return frame_payloads
    
    def get_file_hash(self):
        return self.file_hash