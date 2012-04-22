"""Simple plugin to catch bad commands and report them. Should be loaded last."""

import player_cmd as cmd
from helpers import tell, ops

MC_COMMANDS = ['kill', 'tell']

def on_start():
	cmd.register(r'/(.*)', uncaught_command)

def on_packet(packet, user, to_server):
	return packet

def uncaught_command(message, user, command):
	for mc_cmd in MC_COMMANDS:
		if command.startswith(mc_cmd):
			return False # Do not drop packet
	if user.username in ops():
		tell(user, "Warning: I don't recognise %s" % message)
		return False
	tell(user, "Bad command: %s" % command)
	return True # Drop packet
