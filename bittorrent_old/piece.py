import hashlib

class Piece:
    def __init__(self, index, offset, size, hash):
        self.offset = offset
        self.index = index
        self.size = size
        self.hash = hash
        self.data = b''

    def verify(self):
        if hashlib.sha1(self.data).digest() == self.hash:
            return True