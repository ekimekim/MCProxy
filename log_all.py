import time

f = None

def on_start():
	global f
	f = open("/var/minecraft/logs/all_packets.log", 'a')

def on_packet(packet, user, to_server):
	global f
	f.write('\t'.join([str(time.time()), str(user.addr), repr(packet.original), str(packet)]) + '\n')
	f.flush()
	return packet
