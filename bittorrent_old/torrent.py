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

        self.has = [[0 for j in range(int(self.piece_length / 2**14))] for i in range(len(self.pieces))]

        self.tracker = Tracker(data['announce'], self.info_hash, self.peer_id, 6969)
        
        self.peers = {}
        self.threads = {}

    @staticmethod
    def open(path):
        with open(path, 'rb') as f:
            data = bdecode(f.read())

        return Torrent(data)

    def has_piece_callback(self, data):
        (ip, index, begin, length) = data

        print(f'{ip} has piece {index}')

    def getting_piece_callback(self, data):
        (ip, index, begin, length) = data

        for peer in self.peers:
            if peer != ip:
                self.peers['peer'].cancel(index, begin, length)

        print(f'{ip} is getting piece {index}')

    def got_piece_callback(self, data):
        (ip, index, begin, length, piece) = data

        print(f'{id} got piece {index}')

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

        while True:
            for peer in self.peers:
                status = self.peers[peer].status()

                if status[0] == 'complete':
                    print(f'{peer} got piece {status[1]}:{status[2]}:{status[3]}.')
                    self.has[status[1]][int(status[2] / 2**14)] = 2
                    self.peers[peer].clear()

                elif status[0] == 'failed':
                    print(f'{peer} failed to get piece {status[1]}:{status[2]}:{status[3]}.')
                    self.has[status[1]][int(status[2] / 2**14)] = 0
                    self.peers[peer].clear()

                status = self.peers[peer].status()
                b = False

                if status[0] == 'idle':
                    for j, piece in enumerate(self.has):
                        subpieces = [i for i in range(int(self.piece_length / 2**14)) if piece[i] == 0]

                        for subpiece in subpieces:
                            if self.peers[peer].get(j, subpiece*(2**14), 2**14):
                                print(f'piece {j}:{subpiece*(2**14)}:{2**14} was assigned to {peer}.')
                                self.has[j][subpiece] = 1

                                b = True
                            
                            if b: break

                        if b: break

                

                
