import socket
import struct
import time
from . import messages

class Peer:
    def __init__(self, info_hash, peer_id, ip, port, n_pieces, termination_callback=lambda x: 0):
        self.info_hash = info_hash
        self.peer_id = peer_id

        self.am_choking = 1
        self.am_interested = 0
        self.peer_choking = 1
        self.peer_interested = 0

        self.ip = ip
        self.port = port

        self.n_pieces = n_pieces
        self.has = 0b0

        self.seeking = ('idle', 0, 0, 0, None)

        self.termination_callback = termination_callback

    def mainloop(self):
        self.last_alive = time.time()

        while True:
            data = self.recv()

            if data:
                if data[0]:
                    if data[1] == 0: self.start_choking()
                    elif data[1] == 1: self.stop_choking()
                    elif data[1] == 2: self.start_interested()
                    elif data[1] == 3: self.stop_interested()
                    elif data[1] == 4: self.add_has(data[2])
                    elif data[1] == 5: self.bitfield(data[2])
                    elif data[1] == 6: self.requested_piece(data[2])
                    elif data[1] == 7: self.receive_piece(data[2])
                    elif data[1] == 8: self.cancel_request(data[2])
            
            self.keepalive()

    def send(self, message):
        try:
            self.socket.sendall(message)
            return True

        except:
            self.socket.close()
            self.termination_callback(self.ip)
            return False

    def recv(self):
        length, message_id, content = 0, 0, b''

        try:
            length = int.from_bytes(self.socket.recv(4), 'big')

            if length:
                message_id = int.from_bytes(self.socket.recv(1), 'big')

                if length > 1:
                    content = self.socket.recv(length-1)

            return length, message_id, content

        except:
            return False

    def handshake(self):
        try:
            self.socket = socket.create_connection((self.ip, self.port), 3)
            print(f'connected to {self.ip} on port {self.port}')

        except:
            print(f'failed to connect to {self.ip} on port {self.port}')
            self.termination_callback(self.ip)
            return False

        handshake = messages.pack_handshake(self.info_hash, self.peer_id)
        
        if self.send(handshake):
            try:
                response = messages.unpack_handshake(self.socket.recv(1 + 19 + 8 + 20 + 20))
                return True

            except:
                self.termination_callback(self.ip)
                return False
            
        else:
            self.termination_callback(self.ip)
            return False

    def start_choking(self):
        self.peer_choking = 1
        print(f'{self.ip} has started choking.')

        if self.seeking[0] == 'interested' or self.seeking[0] == 'waiting':
            self.send(messages.pack_uninterested())
            self.seeking = ('failed', self.seeking[1], self.seeking[2], self.seeking[3], None)

    def stop_choking(self):
        self.peer_choking = 0
        print(f'{self.ip} has stopped choking.')

        if self.seeking[0] == 'interested':
            if self.send(messages.pack_request(self.seeking[1], self.seeking[2], self.seeking[3])):
                print(f'requested piece {self.seeking[1]}:{self.seeking[2]}:{self.seeking[3]} from {self.ip}.')
                
                self.seeking = ('waiting', self.seeking[1], self.seeking[2], self.seeking[3], None)

    def start_interested(self):
        self.peer_interested = 1
        print(f'{self.ip} is interested.')

    def stop_interested(self):
        self.peer_interested = 0
        print(f'{self.ip} is not interested.')

    def add_has(self, piece):
        index = int.from_bytes(piece, 'big')

        print(f'{self.ip} has piece {index}.')

        if index < self.n_pieces:
            self.has |= (0b1 << index)

    def bitfield(self, bitfield):
        print(f'{self.ip} sent a bitfield.')

        if len(bitfield) <= self.n_pieces:
            self.has |= int.from_bytes(bitfield, 'little')

        else:
            self.socket.close()
            print(f'connection with {self.ip} terminated.')
            exit()

    def requested_piece(self, data):
        
        print(f'{self.ip} requested.')

    def receive_piece(self, data):
        print(f'{self.ip} sent a piece.')

        if self.seeking[0] == 'waiting':
            self.seeking = ('complete', self.seeking[1], self.seeking[2], self.seeking[3], data)

    def cancel_request(self, data):
        print(f'{self.ip} cancelled.')

    def keepalive(self):
        if time.time() - self.last_alive > 110:
            if self.send(messages.pack_keepalive()):
                print(f'keep alive was sent to {self.ip}.')
                self.last_alive = time.time()

        time.sleep(0.05)

    def status(self):
        return self.seeking

    def clear(self):
        self.seeking = ('idle', 0, 0, 0, None)

    def get(self, index, begin, length):
        if self.seeking[0] == 'idle':
            if self.has & (0b1 << index):
                if self.send(messages.pack_interested()):
                    self.am_interested = 1
                    print(f'interested in piece {self.seeking[1]}:{self.seeking[2]}:{self.seeking[3]} from {self.ip}.')

                    self.seeking = ('interested', index, begin, length, None)

                    if not(self.peer_choking):
                        if self.send(messages.pack_request(index, begin, length)):
                            print(f'requested piece {self.seeking[1]}:{self.seeking[2]}:{self.seeking[3]} from {self.ip}.')

                            self.seeking = ('waiting', index, begin, length, None)

                        else:
                            return False

                    return True

                else:
                    return False

            else:
                return False

        else:
            return False
