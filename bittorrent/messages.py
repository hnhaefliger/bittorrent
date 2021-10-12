import struct

def pack_handshake(info_hash, peer_id):
    return struct.pack('>B19s8s20s20s', 19, b'BitTorrent protocol', b'\x00'*8, info_hash, peer_id)

def unpack_handshake(data):
    return struct.unpack(">B19s8s20s20s", data)

def pack_keepalive():
    return struct.pack('>I', 0)

def pack_interested():
    return struct.pack('>IB', 1, 2)

def pack_uninterested():
    return struct.pack('>IB', 1, 3)

def pack_request(index, begin, length):
    return struct.pack('>IBIII', 13, 6, index, begin, length)

def pack_cancel(index, begin, length):
    return struct.pack('>IBIII', 13, 8, index, begin, length)
