# -*- coding: cp1252 -*-
"""Helper functions for plugins"""

import os, sys, math
from packet_decoder import names as packet_names
from packet_decoder import Packet, SERVER_TO_CLIENT
from config import *

def ops():
	"""Get list of op usernames."""
	ret = open(os.path.join(SERVER_DIR, 'ops.txt')).read().strip().split('\n')
	ret = [unicode(name) for name in ret]
	return ret

def server_cmd(command):
	"""Send a command to server console. May OSError."""
	p = Popen([COMMAND_SCRIPT, command], stderr=PIPE)
	ret = p.wait()
	if ret:
		out, err = p.communicate()
		raise OSError(command, ret, err.read().strip())
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
	return [name[:-4] for name in os.listdir(os.path.join(WORLD_DIR, 'players'))]


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
