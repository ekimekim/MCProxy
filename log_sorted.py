import time
from packet_decoder import names
from os import path

fds = {}
DIR = "/var/minecraft/logs/packets/"

def on_start():
	global fds
	for name in names.values():
		fds[name] = open(path.join(DIR, name), 'a')

def on_packet(packet, user, to_server):
	global fds
	f = fds[packet.name()]
	f.write('\t'.join([str(time.time()), "user->server" if to_server else "server->user", str(user), str(packet.data)]) + '\n')
	f.flush()
	return packet
