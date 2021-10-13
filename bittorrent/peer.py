import socket
import time
from . import messages
import threading

class Peer:
    def __init__(self, info_hash, peer_id, ip, port, n_pieces):
        self.status = 'starting'
        self.last_alive = 0
        self.has = 0x0
        self.piece = None
        self.ip = ip
        self.n_pieces = n_pieces

        self.am_choking = 1
        self.am_interested = 0
        self.peer_choking = 1
        self.peer_interested = 0

        try:
            self.socket = socket.create_connection((ip, port), 3)

            if self.send(messages.pack_handshake(info_hash, peer_id)):
                messages.unpack_handshake(self.socket.recv(1 + 19 + 8 + 20 + 20))
                threading.Thread(target=self.mainloop, daemon=True).start()
                print(f'connected to {ip}')
                self.status = 'running'

            else:
                self.status = 'failed'
        
        except: self.status = 'failed'


    def send(self, message):
        try:
            self.socket.sendall(message)
            return True

        except:
            self.socket.close()
            self.status = 'failed'
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


    def keepalive(self):
        if time.time() - self.last_alive > 110:
            if self.send(messages.pack_keepalive()):
                print(f'keepalive sent to {self.ip}')
                self.last_alive = time.time()
        

    def mainloop(self):
        self.last_alive = time.time()

        while self.status != 'failed':
            data = self.recv()

            if data:
                if data[0]:
                    if data[1] == 0:
                        self.start_choking()
                    elif data[1] == 1:
                        self.stop_choking()
                    elif data[1] == 2:
                        self.start_interested()
                    elif data[1] == 3:
                        self.stop_interested()
                    elif data[1] == 4:
                        self.recv_has(data[2])
                    elif data[1] == 5:
                        self.recv_bitfield(data[2])
                    elif data[1] == 6:
                        self.requested_piece(data[2])
                    elif data[1] == 7:
                        self.receive_piece(data[2])
                    elif data[1] == 8:
                        self.cancel_request(data[2])

            self.keepalive()
        
        self.socket.close()
        print(f'{self.ip} disconnected')

        if self.piece != None:
            self.piece.assigned = False
            self.piece = None

        self.status = 'down'

        
    def start_choking(self):
        print(f'{self.ip} started choking')
        self.peer_choking = 1

        if self.piece != None:
            print(f'{self.ip} failed to get piece {self.piece.index}')
            self.send(messages.pack_uninterested())
            self.am_interested = 0
            self.send(messages.pack_cancel(*self.piece.incomplete))

            self.piece.assigned = False
            self.piece = None

    
    def stop_choking(self):
        print(f'{self.ip} stopped choking')
        self.peer_choking = 0

        if self.piece != None:
            piece = self.piece.incomplete

            if self.am_interested:
                if self.send(messages.pack_request(piece[0], piece[1], piece[2])):
                    print(f'requested bytes {piece[1]}-{piece[1] + piece[2]} of piece {piece[0]} from {self.ip}')
                    pass


    def start_interested(self):
        self.peer_interested = 1

    
    def stop_interested(self):
        self.peer_interested = 0


    def recv_has(self, data):
        index = int.from_bytes(data, 'big')

        if index <= self.n_pieces:
            print(f'{self.ip} has piece {index}')
            self.has |= (0b1 << index)

        else:
            self.status = 'failed'


    def recv_bitfield(self, data):
        print(f'received a bitfield from {self.ip}')
        if len(data) <= self.n_pieces:
            self.has |= int.from_bytes(data, 'little')

        else:
            self.status = 'failed'

    
    def requested_piece(self, data):
        pass


    def receive_piece(self, data):
        if self.am_interested and self.piece != None:
            print(f'recieved part of piece {self.piece.index} from {self.ip}')

            self.piece.add(data)

            if self.piece.complete:
                self.send(messages.pack_uninterested())
                self.am_interested = 0

                self.piece.assigned = False
                self.piece = None

            else:
                piece = self.piece.incomplete
                if self.send(messages.pack_request(piece[0], piece[1], piece[2])):
                    print(f'requested bytes {piece[1]}-{piece[1] + piece[2]} of piece {piece[0]} from {self.ip}')


    def cancel_request(self, data):
        pass


    def get(self, piece):
        if self.piece == None and piece.incomplete and self.status == 'running':
            if self.has & (0b1 << piece.index):
                if self.send(messages.pack_interested()):
                    self.am_interested = 1
                    self.piece = piece
                    piece.assigned = True
                    print(f'assigned piece {piece.index} to {self.ip}')

                    if not(self.peer_choking):
                        piece = self.piece.incomplete

                        if self.send(messages.pack_request(piece[0], piece[1], piece[2])):
                            pass
                            print(f'requested bytes {piece[1]}-{piece[1] + piece[2]} of piece {piece[0]} from {self.ip}')       


                    return True

        return False

    
