from bcoding import bencode, bdecode
from .peer import Peer
from .tracker import Tracker
import threading
import random
import hashlib
import math
import time


class Torrent:
    def __init__(self, data):
        self.info_hash = hashlib.sha1(bencode(data['info'])).digest()
        self.peer_id = hashlib.sha1(bytes(random.getrandbits(20))).digest()
        self.piece_length = data['info']['piece length']
        self.pieces = [data['info']['pieces'][i:i+20] for i in range(0, len(data['info']['pieces']), 20)]
        self.name = data['info']['name']

        if 'length' in data['info']:
            self.files = [[self.name, data['info']['length']]]

        else:
            self.files = [[self.name + '/' + file['path'] + '/' + file['name'], file['length']] for file in data['info']['files']] 

        self.downloaded = 0
        self.uploaded = 0
        self.left = len(self.pieces) * self.piece_length

        self.tracker = Tracker(data['announce'], self.info_hash, self.peer_id, 6969)
        
        self.peers = {}
        self.threads = {}

    @staticmethod
    def open(path):
        with open(path, 'rb') as f:
            data = bdecode(f.read())

        return Torrent(data)

    def peer_failure_callback(self, ip):
        try:
            self.threads[ip].stop()
            del self.threads[ip]
            del self.peers[ip]
            print(f'connection with {ip} terminated.')

        except:
            pass

    def start(self):
        peers = self.tracker.get_peers(self.uploaded, self.downloaded, self.left)

        print(f'found {len(peers)} peers.')

        for peer in peers:
            self.peers[peer['ip']] = Peer(self.info_hash, self.peer_id, peer['ip'], peer['port'], math.ceil(len(self.pieces) / 8), termination_callback=self.peer_failure_callback)

            if not(self.peers[peer['ip']].handshake()):
                del self.peers[peer['ip']]

            else:
                self.threads[peer['ip']] = threading.Thread(target=self.peers[peer['ip']].mainloop, daemon=True)
                self.threads[peer['ip']].start()

        for peer in self.peers:
            self.peers[peer].get(1, 1, 2**14)

        while True:
            time.sleep(1)
