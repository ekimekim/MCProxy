from socket import socket
from socket import error as socket_error
from signal import signal, siginterrupt, SIGIO
from fcntl import fcntl, F_GETFL, F_SETFL, F_SETOWN
from os import O_ASYNC, O_NONBLOCK
from select import select
import sys, os, logging

from config import *

from plugins import plugins

conn_map = {} # Map from in_sock to out_sock (for both directions)
user_map = {} # Map from sock to user data
user_socks = set() # Collection of socks to users
buffers = {} # Map from fd to a read buffer so we always read 256 bytes

def main():

	listener = socket()
	listener.bind(LISTEN_ADDR)
	listener.listen(128)

	logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format=LOG_FORMAT)
	logging.info("Starting up")

	for plugin in plugins[:]: # Note that x[:] is a copy of x
		try:
			logging.debug("Loading plugin: %s", plugin)
			plugin.send = send_packet
			plugin.OnStart()
		except:
			logging.exception("Error initialising plugin %s", plugin)
			plugins.remove(plugin)

	# Register handle_poll as handler for SIGIO
	signal(SIGIO, handle_poll)
	siginterrupt(SIGIO, False)

	daemonise()

	logging.debug("Started up")

	try:
		while 1:
			# Create things
			try:
				user_sock, addr = listener.accept()
			except socket_error: # most likely an E_INTR due to SIGIO
				continue
			logging.debug("New connection from address %s", str(addr))
			srv_sock = socket()
			user = User(addr=addr, user_sock=user_sock, srv_sock=srv_sock)
			srv_sock.connect(SERVER_ADDR)
			# Add things to global data structures
			user_map[user_sock] = user
			user_map[srv_sock] = user
			conn_map[user_sock] = srv_sock
			conn_map[srv_sock] = user_sock
			user_socks.add(user_sock)
			buffers[user_sock] = ''
			buffers[srv_sock] = ''
			# Note we set async last, or else a race cdn could occur: Recieve a signal before setup is done.
			set_async(user_sock)
			set_async(user_sock)
			logging.debug("Now accepting packets from address %s", str(addr))
	except Exception:
		logging.critical("Unhandled exception", exc_info=1)
		sys.exit(1)

sio_queue = 0
def handle_poll(sig, frame):
	"""Gets called when SIGIO is recived. Arguments are required."""
	try:
		logging.debug("Recieved SIGIO")
		global sio_queue
		if sio_queue:
			sio_queue = 2
			return
		else:
			sio_queue = 1
		# The select() call is weird. Basically, r,w,x = select(r,w,x,timeout)
		#  where r,w,x are lists of files. It filters the lists so the output contains:
		#  r: files ready to be read
		#  w: files ready to be written to
		#  x: files with some eXtraordinary condition (rare)
		# Note that i'm looking for files that are readable, out of both the user socks AND the server socks.
		r, w, x = select(conn_map.keys(), [], [], SELECT_TIMEOUT)
		dead = []
		for fd in r:
			if fd in dead:
				continue
			teardown = False
			user = user_map[fd]
			to_server = (fd in user_socks)
			buf = buffers[fd]
			while 1: # Get everything there is to read
				try:
					read = fd.recv(1024)
				except socket_error, ex:
					logging.debug(str(ex))
					break # Stop while loop - we've read all we can
				if not read:
					# Empty read means EOF - i think.
					if to_server:
						logging.info("Connection from %s closed", user.addr)
					else:
						logging.warning("Server connection for %s closed", user.addr)
					teardown = True
					break
				buf += read
			while len(buf) >= 256:
				packet = buf[:256] # Take off first 256 bytes
				buf = buf[256:]
				logging.debug("packet %s %s: %s", "from" if to_server else "to", user.addr,  repr(packet))
				packet = handle_packet(packet, user, to_server)
				conn_map[fd].send(packet)
			buffers[fd] = buf
			if teardown:
				if to_server:
					user_fd = fd
					srv_fd = conn_map[fd]
				else:
					srv_fd = fd
					user_fd = conn_map[fd]
				dead += [user_fd, srv_fd]
				user_fd.close()
				srv_fd.close()
				del conn_map[user_fd]
				del conn_map[srv_fd]
				del user_map[user_fd]
				del user_map[srv_fd]
				del buffers[user_fd]
				del buffers[srv_fd]
				user_socks.remove(user_fd)
				logging.info("Removed socket pair for %s", user.addr)
		if sio_queue == 2:
			sio_queue = 0
			handle_poll(sig,frame)
		else:
			sio_queue = 0
	except Exception:
		logging.critical("Unhandled exception", exc_info=1)
		sys.exit(1)


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
	"""Use low-level unix fcntl calls to set ASYNC and NONBLOCK flags, and direct SIGIO to this process."""
	flags = fcntl(fd, F_GETFL)
	fcntl(fd, F_SETFL, flags | O_ASYNC | O_NONBLOCK)
	fcntl(fd, F_SETOWN, os.getpid())


def pack(packet):
	"""Take a Packet and return a data string"""
	return packet # TODO


def unpack(packet):
	"""Take a data string and return a Packet"""
	return packet # TODO


class User(object):
	"""An object representing a user. Should always contain an addr = (ip, port).
	May contain other things eg. username.
	Add fields by writing to them, eg. user.username = "example"
	"""
	def __init__(self, **kwargs):
		self.__dict__ = kwargs


if __name__=='__main__':
	# Python idiom meaning: if not imported, but run directly:
	main()
