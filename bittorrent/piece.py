import hashlib

class Piece:
    def __init__(self, index, size, hash):
        self.index = index
        self.size = size
        self.hash = hash
        self.assigned = False
        self.pieces = [[i, i+2**14, 0b0] for i in range(0, self.size, 2**14)]
        self.pieces[-1][1] = self.size

    def add(self, data):
        incomplete = int(self.incomplete[1] / (2**14))
        
        if self.pieces[incomplete][2] == 0b0:
            self.pieces[incomplete][2] = data

    @property
    def incomplete(self):
        for piece in self.pieces:
            if piece[2] == 0b0:
                return [self.index, piece[0], piece[1] - piece[0]]

        return False

    @property
    def complete(self):
        if all([piece[2] != 0b0 for piece in self.pieces]):
            total = 0b0

            for piece in self.pieces:
                total <<= 2**17
                total |= piece[2]

                if hashlib.sha1(total).digest() == self.hash:
                    print(f'\tcompleted piece {self.index}')

                    return total

                else:
                    self.pieces = [[i, i+2**14, 0b0] for i in range(0, self.size, 2**14)]
                    self.pieces[-1][1] = self.size

        return False
