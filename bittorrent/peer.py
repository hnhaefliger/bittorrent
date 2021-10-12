import socket
import struct
import time

class Peer:
    def __init__(self, info_hash, peer_id, ip, port, n_pieces):
        self. info_hash = info_hash
        self.peer_id = peer_id

        self.am_choking = 1
        self.am_interested = 0
        self.peer_choking = 1
        self.peer_interested = 0

        self.pstrlen = 19
        self.pstr = "BitTorrent protocol"

        self.ip = ip
        self.port = port

        self.n_pieces = n_pieces
        self.has = 0b0

    def try_to_get(self, index, begin, length):
        if self.has & 0b1 << index:
            self.send(struct.pack('4s1s', b'0x0001', b'0x2'))
            self.am_interested = 1

            if not(self.peer_choking):
                self.send(struct.pack('4s1s', b'0x0001', b'0x1'))
                self.am_choking = 0

                self.send(struct.pack('4s1s4s4s4s', b'0x000d', b'0x6', index.to_bytes(4, 'big'), begin.to_bytes(4, 'big'), length.to_bytes(4, 'big')))
                print(f'requested piece {index} from {self.ip}.')

    def mainloop(self):
        self.last_alive = time.time()

        while True:
            data = self.recv()

            if data:
                if data[0]:
                    if data[1] == 0:
                        self.peer_choking = 1
                        print(f'{self.ip} has started choking.')

                    elif data[1] == 1:
                        self.peer_choking = 0
                        print(f'{self.ip} has stopped choking.')

                    elif data[1] == 2:
                        self.peer_interested = 1
                        print(f'{self.ip} is interested.')

                    elif data[1] == 3:
                        self.peer_interested = 0
                        print(f'{self.ip} is not interested.')

                    elif data[1] == 4:
                        index = int.from_bytes(data[2], 'big')

                        print(f'{self.ip} has piece {index}.')
                        
                        if index < self.n_pieces:
                            self.has |= 0b1 << index

                    elif data[1] == 5:
                        print(f'{self.ip} sent a bitfield.')

                        if len(data[2]) <= self.n_pieces:
                            self.has |= int.from_bytes(data[2], 'big')

                        else:
                            self.socket.close()
                            exit()

                    elif data[1] == 6:
                        print(f'{self.ip} requested.')

                    elif data[1] == 7:
                        print(f'{self.ip} sent a piece.')

                    elif data[1] == 8:
                        print(f'{self.ip} cancelled.')
            
            if self.last_alive - time.time() > 2 * 60:
                print(f'keep alive was sent to {self.ip}.')
                self.send(struct.pack('4s', b'0x0000'))
                self.last_alive = time.time()

    def send(self, message):
        try:
            self.socket.sendall(message)
            return True

        except:
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
            self.socket = socket.create_connection((self.ip, self.port), 2)

        except:
            return False

        handshake = struct.pack(">B{}s8s20s20s".format(self.pstrlen), self.pstrlen, self.pstr.encode('utf-8'), b'\x00'*8, self.info_hash, self.peer_id)
        
        if self.send(handshake):
            try:
                response = self.socket.recv(1 + 19 + 8 + 20 + 20)
                response = struct.unpack(">B{}s8s20s20s".format(self.pstrlen), response)

                return True

            except:
                return False
            
        else:
            return False
