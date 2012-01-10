import time

f = None

def on_start():
	global f
	f = open("log_all.log", 'a')

def on_packet(packet, user, to_server):
	global f
	f.write('\t'.join([str(time.time()), str(user.addr), str(packet)]) + '\n')
	return packet
