from socket import socket
from socket import error as socket_error
from signal import signal, siginterrupt, SIGIO, SIGUSR1
from fcntl import fcntl, F_GETFL, F_SETFL, F_SETOWN
from os import O_ASYNC, O_NONBLOCK
from select import select
from select import error as select_error
import sys, os, time
import simple_logging as logging
import traceback
from thread import allocate_lock
from types import InstanceType

from packet_decoder import stateless_unpack as unpack
from packet_decoder import stateless_pack as pack
from packet_decoder import Packet

from config import *

from plugins import plugins

conn_map = {} # Map from in_sock to out_sock (for both directions)
user_map = {} # Map from sock to user data
user_socks = set() # Collection of socks to users
buffers = {} # Map from fd to a read buffer
send_buffers = {} # Map from fd to a send buffer
sio_lock = allocate_lock() # Lock to emulate NOT having SA_NODEFER set. (grumble python grumble)
listener = None # the main bound listen socket
pending = set() # the sockets that have pending sends

def main():

	global listener
	listener = socket()
	listener.bind(LISTEN_ADDR)
	listener.listen(128)

#	logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format=LOG_FORMAT)
	log_fd = open(LOG_FILE, 'a', 0)
	logging.init(lambda level, msg: log_fd.write("[%f]\t%s\t%s\n" % (time.time(), level, msg)))
	logging.info("Starting up")

	for plugin in plugins[:]: # Note that x[:] is a copy of x
		try:
			logging.debug("Loading plugin: %s", plugin)
			plugin.send = send_packet
			plugin.on_start()
		except:
			logging.exception("Error initialising plugin %s", plugin)
			plugins.remove(plugin)

	# Register handle_poll as handler for SIGIO, and traceback to log on SIGUSR1
	signal(SIGIO, handle_poll)
	signal(SIGUSR1, log_traceback)
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
			logging.info("New connection from address %s", str(addr))
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
			send_buffers[user_sock] = ''
			send_buffers[srv_sock] = ''
			# Note we set async last, or else a race cdn could occur: Recieve a signal before setup is done.
			set_async(user_sock)
			set_async(srv_sock)
			logging.debug("Now accepting packets from address %s", str(addr))
			# SIGIO won't be sent if the change occured before set_async, so to be safe:
			handle_poll(0, None)
	except Exception:
		logging.critical("Unhandled exception", exc_info=1)
		listener.close()
		sys.exit(1)


sio_repeat = False
def handle_poll(sig, frame):
	"""Gets called when SIGIO is recived. Arguments are required."""
	try:
		global sio_lock
		global sio_repeat
		acquired = sio_lock.acquire(False)
		if not acquired:
			logging.debug("SIGIO ignored, lock active")
			sio_repeat = True
			return
		if sig != SIGIO:
			logging.debug("Recieved SIGIO (repeated)")
		else:
			logging.debug("Recieved SIGIO")
		sio_repeat = False # Not safe to reset this after select() but now it's fine

		# The select() call is weird. Basically, r,w,x = select(r,w,x,timeout)
		#  where r,w,x are lists of files. It filters the lists so the output contains:
		#  r: files ready to be read
		#  w: files ready to be written to
		#  x: files with some eXtraordinary condition (rare)
		# Note that i'm looking for files that are readable, out of both the user socks AND the server socks.
		while 1:
			try:
				r, w, x = select(conn_map.keys(), pending, [], SELECT_TIMEOUT)
			except select_error, ex:
				code, msg = ex
				if msg != 'Interrupted system call':
					raise
			else:
				break

		dead = []

		logging.debug("%s\n%s", r, w)

		for fd in w:
			buf = send_buffers[fd]
			try:
				n = fd.send(buf)
			except socket_error:
				n = 0
			if n != len(buf):
				buf = buf[n:]
				pending.add(send_fd)
			else:
				buf = ''
			send_buffers[fd] = buf
			
		for fd in r:
			logging.debug("reading from socket %s", fd)
			if fd in dead:
				logging.debug("fd already down - skipping")
				continue
			teardown = False
			user = user_map[fd]
			to_server = (fd in user_socks)
			buf = buffers[fd]
			logging.debug("Buffer before read: length %d", len(buf))
			while 1: # Get everything there is to read
				try:
					read = fd.recv(1024)
				except socket_error, ex:
					break # Stop while loop - we've read all we can
				if not read:
					# Empty read means EOF - i think.
					if to_server:
						logging.info("Connection from %s closed", user.addr)
					else:
						logging.info("Server connection for %s closed", user.addr)
					teardown = True
					break
				buf += read

			logging.debug("Buffer after read: length %d", len(buf))
			while 1:
				try:
					packet, buf = unpack(buf, to_server)
				except: # Undefined exception inherited from packet_decoder
					logging.exception("Bad packet %s %s: %s", "from" if to_server else "to", user.addr, repr(buf))
					teardown = True
					logging.warning("Dropping connection for %s", user.addr)
					break

				if packet is None:
					break

#				logging.debug("packet %s %s: %s", "from" if to_server else "to", user.addr,  packet)
				packets = handle_packet(packet, user, to_server)
				try:
					out_bytestr = ''.join([pack(packet, to_server) for packet in packets])
				except: # Undefined exception inherited from packet_decoder
					logging.exception("Bad packet object while packing packet %s %s: %s", "from" if to_server else "to", user.addr, packet)
					teardown = True
					logging.warning("Dropping connection for %s", user.addr)
					break

				send_fd = conn_map[fd]
				buf = send_buffers[send_fd]
				buf += out_bytestr
				try:
					n = send_fd.send(buf)
				except socket_error:
					n = 0
				if n != len(buf):
					buf = buf[n:]
					pending.add(send_fd)
				else:
					buf = ''

				send_buffers[send_fd] = buf

			logging.debug("Buffer after decode: length %d", len(buf))
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

		sio_lock.release()
		if sio_repeat:
			logging.debug("Extra SIGIO occured during handling, repeat")
			handle_poll(0,frame)
		logging.debug("exiting handler")
	except Exception:
		logging.critical("Unhandled exception", exc_info=1)
		listener.close()
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


def handle_packet(packet, user, to_server):
	"""
		packet: The packet object recieved
		to_server: True if packet is user->server, else False.
		addr: The user packet is being sent from/to.
	Return a list of packet objects to send to out stream (normally [the same packet])"""
	packets = [packet]
	for plugin in plugins:
		old_packets = packets
		packets = []
		for packet in old_packets:
			try:
				ret = plugin.on_packet(packet, user, to_server)
				ispacket = lambda x: type(x) == InstanceType and isinstance(x, Packet)
				if type(ret) == list:
					assert all(ispacket(x) for x in ret), "Return value not list of packets: %s" % repr(ret)
					packets += ret
				elif ispacket(ret):
					packets.append(ret)
				else:
					assert False, "Return value not packet or list: %s" % repr(ret)
			except:
				logging.exception("Error in plugin %s" % plugin)
				packets.append(packet)
	return packets


def send_packet(packet, user, to_server):
	"""Takes same args as handle_packet.
	Simulates that kind of packet having been recived and passes it on as normal"""
	packets = handle_packet(packet, user, to_server)
	
	try:
		out_bytestr = ''.join([pack(packet, to_server) for packet in packets])
	except: # Undefined exception inherited from packet_decoder
		logging.exception("Bad packet object while packing generated packet %s %s: %s", "from" if to_server else "to", user.addr, packet)
		raise # Will be caught as a failure of the plugin sending it.

	if to_server:
		user.srv_sock.send(out_bytestr)
	else:
		user.user_sock.send(out_bytestr)


def set_async(fd):
	"""Use low-level unix fcntl calls to set ASYNC and NONBLOCK flags, and direct SIGIO to this process."""
	flags = fcntl(fd, F_GETFL)
	fcntl(fd, F_SETFL, flags | O_ASYNC | O_NONBLOCK)
	fcntl(fd, F_SETOWN, os.getpid())


def log_traceback(sig, frame):
	tb = traceback.format_stack()
	tb = ''.join(tb)
	logging.info("Recieved SIGUSR1, printing traceback:\n" + tb)


class User(object):
	"""An object representing a user. Should always contain an addr = (ip, port).
	Should also have user_sock and srv_sock.
	May contain other things eg. username.
	Add fields by writing to them, eg. user.username = "example"
	"""
	def __init__(self, **kwargs):
		self.__dict__ = kwargs


if __name__=='__main__':
	# Python idiom meaning: if not imported, but run directly:
	main()
