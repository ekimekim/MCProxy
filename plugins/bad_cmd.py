"""Simple plugin to catch bad commands and report them. Should be loaded last."""

import player_cmd as cmd
from helpers import tell

MC_COMMANDS = ['kill', 'tell']

def on_start():
	cmd.register(r'/(.*)', uncaught_command)

def on_packet(packet, user, to_server):
	return packet

def uncaught_command(message, user, command):
	if command in MC_COMMANDS or user.username in ops():
		return False # Do not drop packet
	tell(user, "Bad command: %s" % command)
	return True # Drop packet
