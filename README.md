# bittorrent

A simple bittorrent client based on [the unofficial bittorrent spec](https://wiki.theory.org/index.php/BitTorrentSpecification#Tracker_HTTP.2FHTTPS_Protocol) as well as [this description](http://www.dsc.ufcg.edu.br/~nazareno/bt/bt.htm).

Usage:

```python3
import bittorrent

test = bittorrent.Torrent.open('ubuntu-20.04.3-desktop-amd64.iso.torrent')
test.start()
```