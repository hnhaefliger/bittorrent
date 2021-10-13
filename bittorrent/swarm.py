import hashlib
import random

from .tracker import Tracker
from .peer import Peer


class Swarm:
    def __init__(self, info_hash, tracker, file):
        self.info_hash = info_hash
        self.peer_id = hashlib.sha1(bytes(random.getrandbits(20))).digest()
        self.tracker = Tracker(tracker, info_hash, self.peer_id, 6969)
        self.file = file
        file.swarm = self

        self.peers = {}

    def update(self):
        self.peers = {peer: self.peers[peer] for peer in self.peers if self.peers[peer].status != 'down'}

        if len(self.peers) < 40:
            self.add_peers(self.tracker.get_peers(*self.file.status))

    def add_peers(self, peers):
        for peer in peers:
            if peer['ip'] not in self.peers:
                self.peers[peer['ip']] = Peer(self.info_hash, self.peer_id, peer['ip'], peer['port'], len(self.file.pieces))

    def get(self, piece):
        for peer in self.peers:
            if self.peers[peer].get(piece):
                break


