
import time

from config import *
from os import path
f = None

def on_start():
	global f
	f = open(path.join(LOG_DIR, "all_packets.log"), 'a')

def on_packet(packet, user, to_server):
	global f
	f.write('\t'.join([str(time.time()), "user->server" if to_server else "server->user", str(user), repr(packet.original) if hasattr(packet, 'original') else 'FABRICATED', str(packet)]) + '\n')
	f.flush()
	return packet
