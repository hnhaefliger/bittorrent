from .piece import Piece

class File:
    def __init__(self, data):
        self.swarm = None

        self.piece_length = data['info']['piece length']

        pieces = [data['info']['pieces'][i:i+20] for i in range(0, len(data['info']['pieces']), 20)]
        self.pieces = [Piece(i, self.piece_length, piece, ) for i, piece in enumerate(pieces)]

        self.name = data['info']['name']

        with open(self.name, 'w+') as f:
            pass

        self.completed = 0

        if 'length' in data['info']:
            self.files = [[self.name, data['info']['length']]]

        else:
            self.files = [[self.name + '/' + file['path'] + '/' + file['name'], file['length']] for file in data['info']['files']]


    @property
    def status(self):
        return [self.completed * self.piece_length, len(self.pieces) * self.piece_length, 0]

    
    def update(self):
        remove = []

        for piece in self.pieces:
            if piece.verified:
                with open(self.name, 'r+b') as f:
                    f.seek(piece.index * self.piece_length)
                    f.write(piece.verified)

                self.completed += 1
                remove.append(piece)
            
            elif not(piece.assigned):
                self.swarm.get(piece)

        for piece in remove:
            self.pieces.remove(piece)