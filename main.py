from socket import socket
from signal import signal, SIGIO
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_ASYNC, O_NONBLOCK
import sys, os, logging

from config import *

from plugins import plugins

conn_map = {} # Map from in_sock to out_sock (for both directions)
user_map = {} # Map from sock to user data
user_socks = set() # Collection of socks to users

def main():

	listener = socket()
	listener.bind(LISTEN_ADDR)
	listener.listen(128)

	logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format=LOG_FORMAT)
	logging.info("Starting up")

	for plugin in plugins[:]: # Note that x[:] is a copy of x
		try:
			plugin.send = send_packet
			plugin.OnStart()
		except:
			logging.exception("Error initialising plugin %s", plugin)
			plugins.remove(plugin)

	# Register handle_poll as handler for SIGIO
	signal(SIGIO, handle_poll)

	daemonise()

	try:
		while 1:
			# Create things
			user_sock, addr = listener.accept()
			srv_sock = socket()
			user = User(addr=addr, user_sock=user_sock, srv_sock=srv_sock)
			srv_sock.connect(SERVER_ADDR)
			# Add things to global data structures
			user_map[user_sock] = user
			user_map[srv_sock] = user
			conn_map[user_sock] = srv_sock
			conn_map[srv_sock] = user_sock
			user_socks.add(user_sock)
			# Note we set async last, or else a race cdn could occur: Recieve a signal before setup is done.
			set_async(user_sock)
			set_async(user_sock)
	except:
		logging.critical("Unhandled exception", exc_info=1)
		raise


def handle_poll(sig, frame):
	"""Gets called when SIGIO is recived. Arguments are required."""
	try:
		# The select() call is weird. Basically, r,w,x = select(r,w,x,timeout)
		#  where r,w,x are lists of files. It filters the lists so the output contains:
		#  r: files ready to be read
		#  w: files ready to be written to
		#  x: files with some eXtraordinary condition (rare)
		# Note that i'm looking for files that are readable, out of both the user socks AND the server socks.
		r, w, x = select(conn_map.keys(), [], [], SELECT_TIMEOUT)
		for fd in r:
			user = user_map[fd]
			to_server = (fd in user_socks)
			while 1:
				try:
					packet = fd.recv(256)
				except IOError:
					break # Stop while loop
				packet = handle_packet(packet, user, to_server)
				conn_map[fd].write(packet)
	except:
		logging.critical("Unhandled exception", exc_info=1)
		raise


def daemonise():
	"""Detach from current session and run in background.
	This is some unix black magic, best ignore it."""
	sys.stdin.close()
	sys.stdout.close()
	sys.stderr.close()
	os.chdir("/")
	if os.fork():
		sys.exit(0)
	if os.fork():
		sys.exit(0)


def handle_packet(packet, user, to_server, no_unpack=False):
	"""
		packet: The string data recieved
		to_server: True if packet is user->server, else False.
		addr: The user packet is being sent from/to.
		no_unpack: optional. skip unpack step.
	Return a string to send to out stream (normally the same packet)"""
	logging.info("Packet: %s" % repr(packet))
	if not no_unpack:
		packet = unpack(packet)
	packets = [packet]
	for plugin in plugins:
		try:
			old_packets = packets[:]
			packets = []
			for packet in old_packets:
				ret = plugin.OnPacket(packet, user, to_server)
				if type(ret) == list:
					packets += ret
				else:
					packets.append(ret)
		except:
			logging.exception("Error in plugin %s" % plugin)
	packets = map(pack, packets)
	return ''.join(packets)


def send_packet(packet, user, to_server):
	"""Takes same args as handle_packet, but packet should be a Packet.
	Simulates that kind of packet having been recived and passes it on as normal"""
	packets = handle_packet(packet, user, to_server, no_unpack=True)
	if to_server:
		user.srv_sock.send(packets)
	else:
		user.user_sock.send(packets)


def set_async(fd):
	"""Use low-level unix fcntl calls to set ASYNC and NONBLOCK flags"""
	flags = fcntl(fd, F_GETFL)
	fcntl(fd, F_SETFL, flags | O_ASYNC | O_NONBLOCK)


class User(object):
	"""An object representing a user. Should always contain an addr = (ip, port).
	May contain other things eg. username.
	Add fields by writing to them, eg. user.username = "example"
	"""
	pass


if __name__=='__main__':
	# Python idiom meaning: if not imported, but run directly:
	main()
