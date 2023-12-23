import hashlib

class FileWriter:
    def __init__(self, frames: list[bytes], file_name: str) -> None:
        self.frames = frames
        self.file_name = 'received/'+file_name
        
    def write_file(self):
        original_file = bytes()
        for frame in self.frames:
            original_file += frame
        with open(self.file_name, 'wb') as result:
            result.write(original_file)
        print(f'[!] Received file hash: {hashlib.md5(original_file).hexdigest()}')