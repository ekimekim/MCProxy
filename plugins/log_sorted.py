
import time
from packet_decoder import names

from config import *
import os 

fds = {}
DIR = os.path.join(LOG_DIR, "packets")
if not os.path.exists(DIR):
    os.makedirs(DIR)


def on_start():
	global fds
	for name in names.values():
		fds[name] = open(os.path.join(DIR, name), 'a')

def on_packet(packet, user, to_server):
	global fds
	f = fds[packet.name()]
	f.write('\t'.join([str(time.time()), "user->server" if to_server else "server->user", str(user), str(packet.data)]) + '\n')
	f.flush()
	return packet
