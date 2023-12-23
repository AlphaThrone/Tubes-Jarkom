class SegmentFlag:
    def __init__(self, syn: bool=False, ack: bool=False, fin: bool=False) -> None:
        self.syn = syn
        self.ack = ack
        self.fin = fin
        
    def get_flag_bytes(self) -> bytes:
        bit = 0b0000
        if (self.syn):
            bit = bit | 0b0010
        if (self.ack):
            bit = bit | 0b1000
        if (self.fin):
            bit = bit | 0b0001
        return bit.to_bytes()