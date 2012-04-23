# -*- coding: cp1252 -*-
"""Helper functions for plugins"""

import os, sys, math
from packet_decoder import names as packet_names
from packet_decoder import Packet, SERVER_TO_CLIENT
from config import *

def ops():
	"""Get list of op usernames."""
	p = os.path.join(SERVER_DIR, 'ops.txt')
	ret = []
	if os.path.isfile(p):
		f = open(p, 'r')
		for line in f:
			ret.append(unicode(line.lower()))
	return ret

def server_cmd(command):
	command = command.strip()
	#strip of the leading '/' of the command, not needed.
	if command[0] == '/':
		command = command[1:]

	logging.info("Sending server command: " + command)
	send = "screen -S " + SERVER_SCREEN_NAME + " -X stuff \"" + command + "\n\""
	status = os.system(send)
	logging.info("Exit Status: " + str(status))
	if status != 0:
		logging.critical("Failed to send command")
	return


def point_dist(p, q):
	"""Gets distance between points a and b. They should both be tuples of the same length."""
	if len(p) != len(q):
		raise ValueError("Lengths don't match", p, q)
	return math.sqrt(sum((a-b)**2 for a,b in zip(p,q)))

colors = {
		'black': u'0',
		'dark blue': u'1',
		'dark green': u'2',
		'dark cyan': u'3',
		'dark red': u'4',
		'purple': u'5',
		'gold': u'6',
		'gray': u'7',
		'dark gray': u'8',
		'blue': u'9',
		'green': u'a',
		'cyan': u'b',
		'red': u'c',
		'pink': u'd',
		'yellow': u'e',
		'white': u'f'
	}
def color(name):
	"""Takes a color name and returns the string needed to turn the chat message that color."""
	if name not in colors:
		raise ValueError('Bad color %s' % repr(name))
	return u'§' + colors[name]


def all_users():
	"""Returns list of users who ever played on the server"""
	names = []
	for world in WORLD_DIRS:
		for name in os.listdir(os.path.join(world, 'players')):
			n = name[:len(name)-4]
			if n not in names:
				names.append(u'' + n)
	names.sort()
	return names


def tell(user, message, prefix=''):
	"""Send a server message to user.
	Note: Splits multiline messages. See prefix, below.
	Optional args:
		prefix: Add given prefix to every line sent, eg '<server>: '.
	"""
	message = unicode(message)

	reverse = dict([(y,x) for x,y in packet_names.items()])
	for line in message.split('\n'):
		packet = Packet()
		packet.ident = reverse['Chat message']
		packet.direction = SERVER_TO_CLIENT
		packet.data = {'text': line}
		send_packet(packet, user, False)
