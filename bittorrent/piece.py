import hashlib
import math

class Piece:
    def __init__(self, index, size, hash):
        self.index = index
        self.size = size
        self.n_pieces = math.ceil(self.size / (2**14))

        self.hash = hash
        self.assigned = False
        self.verified = False

        self.pieces = [[i*(2**14), (i+1)*(2**14), b''] for i in range(self.n_pieces)]
        self.pieces[-1][1] = self.size

    def add(self, data):
        index = int.from_bytes(data[:4], byteorder='big')
        begin = int.from_bytes(data[4:8], byteorder='big')

        block = data[8:]

        if index == self.index:
            incomplete = self.incomplete
            i = int(incomplete[1] / (2**14))

            if len(block) == incomplete[2] and begin == incomplete[1]:
                if self.pieces[i][2] == b'':
                    self.pieces[i][2] = block
                    return True

        return False

    @property
    def incomplete(self):
        for piece in self.pieces:
            if piece[2] == b'':
                return [self.index, piece[0], piece[1] - piece[0]]

        return False

    @property
    def complete(self):
        if all([piece[2] != b'' for piece in self.pieces]):
            print(f'verifying piece {self.index}')
            total = b''

            for piece in self.pieces:
                total += piece[2]

            if hashlib.sha1(total).digest() == self.hash:
                print(f'completed piece {self.index}')

                self.verified = total

                return True

            else:
                print(f'piece {self.index} was invalid')
                self.pieces = [[i*(2**14), (i+1)*(2**14), b''] for i in range(self.n_pieces)]
                self.pieces[-1][1] = self.size

        return False
