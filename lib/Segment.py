from lib.SegmentFlag import SegmentFlag;
import struct

class Segment:
    def __init__(self, flags: SegmentFlag = SegmentFlag(), seq_num: int = 0, ack_num: int= 0, 
                 checksum: bytes = b'\x00\x00', payload: bytes = b'') -> None:
        self.flags = flags
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.checksum = checksum
        self.payload = payload
    
    @staticmethod
    def syn(seq_num: int) -> 'Segment':
        return Segment(flags=SegmentFlag(syn=True), seq_num=seq_num)
    
    @staticmethod
    def ack(seq_num: int, ack_num: int) -> 'Segment':
        return Segment(flags=SegmentFlag(ack=True), seq_num=seq_num, ack_num=ack_num)
    
    @staticmethod
    def syn_ack() -> 'Segment':
        return Segment(flags=SegmentFlag(syn=True, ack=True))
        
    @staticmethod
    def fin(file_name: str) -> 'Segment':
        return Segment(flags=SegmentFlag(fin=True), payload=file_name.encode('utf-8'))
    
    @staticmethod
    def fin_ack() -> 'Segment':
        return Segment(flags=SegmentFlag(fin=True, ack=True))
    
    #one compliment check
    def __calculate_checksum(self) -> bytes:
        checksum = 0
        for byte in self.payload:
            checksum += byte
            checksum = (checksum & 0xFFFF) + (checksum >> 16)
        checksum = (~checksum & 0xFFFF).to_bytes(2, byteorder='big')
        return checksum
    
    def update_checksum(self) -> None:
        self.checksum = self.__calculate_checksum()
    
    def is_valid_checksum(self) -> bool:
        calculated_checksum = self.__calculate_checksum()
        return calculated_checksum == self.checksum
    
    def get_segment_bytes(self) -> bytes:
        seqnum_packed = struct.pack('<I',self.seq_num)
        acknum_packed = struct.pack('<I',self.ack_num)
        empty_padding = b'\x00'
        flag_padding_checksum = self.flags.get_flag_bytes() + empty_padding + self.checksum
        packed_payload = self.payload
        return seqnum_packed + acknum_packed + flag_padding_checksum + packed_payload

# with open('test.md', 'rb') as file:
#     #read the first 100 bytes in the file
#     #empty param in read() will read entire file
#     file_bytes = file.read(100)
# segment = Segment(SegmentFlag(True),65468,56465,payload=file_bytes)
# pack = struct.pack('i',segment.seq_num)
# print("seq_num:  " + str(struct.pack('<I',segment.seq_num)))
# print("ack_num:  " + str(struct.pack('<I',segment.ack_num)))
# print("FlagsDKK: " + str(segment.flags.get_flag_bytes() + b'\x00' + segment.checksum))
# segment.update_checksum()
# print("checksum: " + str(segment.checksum))
# print("FlagsDKK: " + str(segment.flags.get_flag_bytes() + b'\x00' + segment.checksum))
# print("payload:  " + str(segment.payload))
# # print(segment.get_segment_bytes()[:4]) seq_num
# # print(segment.get_segment_bytes()[4:8]) ack_num
# # print(segment.get_segment_bytes()[8:9]) flags
# # print(segment.get_segment_bytes()[9:10]) empty padding
# print("checksum: " + str(segment.get_segment_bytes()[10:12]))
# # print(segment.get_segment_bytes()[12:]) payload
# print("Result: ")
# print(segment.get_segment_bytes())