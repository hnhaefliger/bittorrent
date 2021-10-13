from bcoding import bencode, bdecode
import hashlib

from .swarm import Swarm
from .file import File


class Torrent:
    def __init__(self, data):
        self.info_hash = hashlib.sha1(bencode(data['info'])).digest()

        self.file = File(data)
        self.swarm = Swarm(self.info_hash, data['announce'], self.file)

    @staticmethod
    def open(path):
        with open(path, 'rb') as f:
            data = bdecode(f.read())

        return Torrent(data)

    def start(self):
        while True:
            self.swarm.update()
            self.file.update()

                

                
