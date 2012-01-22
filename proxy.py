from socket import socket
from socket import error as socket_error
from select import select
from select import error as select_error
import sys, os, time, traceback, errno
import simple_logging as logging
from types import InstanceType

import usrtrace

from packet_decoder import stateless_unpack as unpack
from packet_decoder import stateless_pack as pack
from packet_decoder import Packet

from config import *

from plugins import plugins

conn_map = {} # Map from in_sock to out_sock (for both directions)
user_map = {} # Map from sock to user data
user_socks = set() # Collection of socks to users
read_buffers = {} # Map from fd to a read buffer
send_buffers = {} # Map from fd to a send buffer, if any.
listener = None # the main bound listen socket

def main():

	global listener
	listener = socket()
	listener.bind(LISTEN_ADDR)
	listener.listen(128)
	listener.setblocking(0)

#	logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format=LOG_FORMAT)
	log_fd = open(LOG_FILE, 'a', 0)
	logging.init(lambda level, msg: (level != 'debug') and (log_fd.write("[%f]\t%s\t%s\n" % (time.time(), level, msg))))
	logging.info("Starting up")

	for plugin in plugins[:]: # Note that x[:] is a copy of x
		try:
			logging.debug("Loading plugin: %s", plugin)
			plugin.send = send_packet
			plugin.cmd = server_cmd
			plugin.on_start()
		except:
			logging.exception("Error initialising plugin %s", plugin)
			plugins.remove(plugin)

	daemonise()
	sys.stdout = log_fd
	sys.stderr = log_fd

	logging.debug("Started up")

	try:
		while 1:

			try:
				r, w, x = select(conn_map.keys() + [listener], send_buffers.keys(), [])
			except select_error, ex:
				if ex.errno == errno.EINTR:
					continue
				raise

			dead = [] # Keeps track of fds in r, w that get dropped, so we know when not to bother.

			for fd in w:
				if fd in dead:
					logging.debug("fd already down - skipping")
					continue

				buf = send_buffers[fd]

				try:
					n = fd.send(buf[:MAX_SEND])
				except socket_error, ex:
					if ex.errno == errno.EINTR:
						n = 0
					elif ex.errno in (errno.ECONNRESET, errno.EPIPE, errno.ENETDOWN, errno.ENETUNREACH, errno.ENOBUFS):
						# These are all socket failure conditions, drop the connection
						user = user_map[fd]
						logging.warning("Dropping connection for %s due to send error to %s", user, "user" if fd in user_socks else "server", exc_info=1)
						dead += [fd, conn_map[fd]]
						drop_connection(user)
						continue
					else:
						raise

				assert n <= len(buf)
				if n < len(buf):
					send_buffers[fd] = buf[n:]
				else:
					del send_buffers[fd]

			for fd in r:
				if fd in dead:
					logging.debug("fd already down - skipping")
					continue

				if fd is listener:
					# Then Cicero asks what did the Night Mother say?
					new_connection()
					continue

				buf = read_buffers[fd]
				to_server = (fd in user_socks)
				user = user_map[fd]

				logging.debug("Buffer before read: length %d", len(buf))
				try:
					read = fd.recv(MAX_RECV)
				except socket_error, ex:
					if ex.errno == errno.EINTR:
						continue
					if ex.errno in (errno.ECONNRESET, errno.ETIMEDOUT, errno.ENOBUFS, errno.ENOMEM):
						# These are all socket failure conditions, drop the connection
						logging.warning("Dropping connection for %s due to recv error from %s", user, "user" if to_server else "server", exc_info=1)
						dead += [fd, conn_map[fd]]
						drop_connection(user)
						continue
				if not read:
					# Empty read means EOF - i think.
					if to_server:
						logging.info("Connection from %s closed", user)
					else:
						logging.info("Server connection for %s closed", user)
					dead += [fd, conn_map[fd]]
					drop_connection(user)
					continue

				buf += read
				logging.debug("Buffer after read: length %d", len(buf))

				# Decode as many packets as we can
				while 1:
					try:
						packet, buf = unpack(buf, to_server)
					except: # Undefined exception inherited from packet_decoder
						logging.exception("Bad packet %s %s:\n%s", "from" if to_server else "to", user, hexdump(buf))
						logging.warning("Dropping connection for %s due to bad packet from %s", user, "user" if to_server else "server")
						dead += [fd, conn_map[fd]]
						drop_connection(user)
						break
					if packet is None:
						# Couldn't decode, need more read first - we're done here.
						break

					packets = handle_packet(packet, user, to_server)
					packed = []
					for packet in packets:
						try:
							packed.append(pack(packet, to_server))
						except: # Undefined exception inherited from packet_decoder
							logging.warning("Bad packet object while packing packet %s %s: %s", "from" if to_server else "to", user, packet, exc_info=1)

					out_bytestr = ''.join(packed)

					# Append resulting bytestr to write buffer, to be sent later.
					send_fd = conn_map[fd]
					write_buf = send_buffers.get(send_fd, '')
					write_buf += out_bytestr
					send_buffers[send_fd] = write_buf

				if fd not in dead:
					logging.debug("Buffer after decode: length %d", len(buf))
					read_buffers[fd] = buf

	except Exception:
		logging.critical("Unhandled exception", exc_info=1)
		listener.close()
		sys.exit(1)


def drop_connection(user):
	user_fd = user.user_sock
	srv_fd = user.srv_sock
	user_fd.close()
	srv_fd.close()
	del conn_map[user_fd]
	del conn_map[srv_fd]
	del user_map[user_fd]
	del user_map[srv_fd]
	del read_buffers[user_fd]
	del read_buffers[srv_fd]
	user_socks.remove(user_fd)
	if user_fd in send_buffers:
		del send_buffers[user_fd]
	if srv_fd in send_buffers:
		del send_buffers[srv_fd]
	logging.info("Removed socket pair for %s", user)


def new_connection():
	try:
		user_sock, addr = listener.accept()
	except socket_error, ex:
		if ex.errno == errno.EINTR: # Harmless - interrupted. Leave it be and it will be tried again next pass.
			return
		raise
	logging.info("New connection from address %s", str(addr))
	# Setup objects
	srv_sock = socket()
	user = User(addr=addr, user_sock=user_sock, srv_sock=srv_sock)
	srv_sock.connect(SERVER_ADDR)
	user_sock.setblocking(0)
	srv_sock.setblocking(0)
	# Add things to global data structures
	user_map[user_sock] = user
	user_map[srv_sock] = user
	conn_map[user_sock] = srv_sock
	conn_map[srv_sock] = user_sock
	user_socks.add(user_sock)
	read_buffers[user_sock] = ''
	read_buffers[srv_sock] = ''
	logging.debug("Now accepting packets from address %s", str(addr))


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
	ispacket = lambda x: type(x) == InstanceType and isinstance(x, Packet)

	packets = [packet]
	for plugin in plugins:
		old_packets = packets
		packets = []
		for packet in old_packets:
			try:
				ret = plugin.on_packet(packet, user, to_server)
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
		logging.exception("Bad packet object while packing generated packet %s %s: %s", "from" if to_server else "to", user, packet)
		raise # Will be caught as a failure of the plugin sending it.

	fd = user.srv_sock if to_server else user.user_sock
	write_buf = send_buffers.get(fd, '')
	write_buf += out_bytestr
	send_buffers[fd] = write_buf


def hexdump(s):
	"""Returns a string representation of a bytestring"""
	STEP = 18 # Optimal per-line for screen width 80
	PRINTING = [chr(n) for n in range(32,127)]
	result = ''
	for offset in range(0, len(s), STEP):
		slice = s[offset:offset+STEP]
		result += ' '.join(['%02x' % ord(c) for c in slice])
		result += '        '
		result += ''.join([c if c in PRINTING else '.' for c in slice])
		result += '\n'
	return result


def log_traceback(sig, frame):
	tb = traceback.format_stack()
	tb = ''.join(tb)
	logging.info("Recieved SIGUSR1, printing traceback:\n" + tb)


def server_cmd(command):
	"""Send a command to server console. May OSError."""
	p = Popen([COMMAND_SCRIPT, command], stderr=PIPE)
	ret = p.wait()
	if ret:
		out, err = p.communicate()
		raise OSError(command, ret, err.read().strip())
	return


class User(object):
	"""An object representing a user. Should always contain an addr = (ip, port).
	Should also have user_sock and srv_sock.
	May contain other things eg. username.
	Add fields by writing to them, eg. user.username = "example"
	"""
	def __init__(self, **kwargs):
		self.__dict__ = kwargs
	def __str__(self):
		d = self.__dict__ # I'm lazy and don't like underscores
		if 'addr' not in d:
			return repr(self)
		elif 'username' not in d:
			return "<unknown>@%s:%s" % self.addr
		else:
			return "%s@%s:%s" % ((self.username,) + self.addr)


if __name__=='__main__':
	# Python idiom meaning: if not imported, but run directly:
	main()
