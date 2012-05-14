
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """A plugin to replicate the ban-by-ip functionality that exists
in the basic server, which doesn't work with the proxy (as all connections come from localhost).
Reads ban list from the server files. Refreshes every second."""


import os, logging
import schedule
from helpers import send_packet
from packet_decoder import Packet
from config import SERVER_DIR


bans = None
ban_file = os.path.join(SERVER_DIR, "banned-ips.txt")

INTERVAL = 1 # Seconds between refresh


def on_start():
	load_bans()


def load_bans():
	global bans
	try:
		new_bans = open(ban_file, 'rU').read().split('\n')
	except IOError, ex:
		if bans is None:
			raise
		logging.warning("Failed to refresh ban file:", exc_info=True)
	else:
		bans = new_bans

	schedule.register(INTERVAL, load_bans) # Repeat self after INTERVAL


def on_packet(packet, user, to_server):
	if to_server and packet.name() == 'Handshake':
		ip, port = user.addr
		if ip in bans:
			packet = Packet("Disconnect", reason="No U")
			send_packet(packet, user, False)
			return []
	return packet
