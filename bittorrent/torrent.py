from .bencode import decode

class Torrent:
    def __init__(self, path):
        self.path = path

        with open(path, 'rb') as f:
            data = decode(f.read())

        
            