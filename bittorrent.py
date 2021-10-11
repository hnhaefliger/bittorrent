import bittorrent

test = bittorrent.Torrent.open('ubuntu-20.04.3-desktop-amd64.iso.torrent')
test.start()