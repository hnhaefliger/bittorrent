import requests
from bcoding import bdecode

class Tracker:
    def __init__(self, url, info_hash, peer_id, port):
        self.url = url
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.port = port

    def get_peers(self, uploaded, downloaded, left):
        response = requests.get(self.url, params={
            'info_hash': self.info_hash,
            'peer_id': self.peer_id,
            'uploaded': uploaded,
            'downloaded': downloaded,
            'left': left,
            'port': self.port,
            'event': 'started',
        })

        return bdecode(response.content)['peers']
