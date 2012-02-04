# -*- coding: cp1252 -*-
"""Helper functions for plugins"""

import os
from proxy import send_packet
from proxy import server_cmd as cmd
from packet_decoder import names as packet_names
from config import *

def ops():
	"""Get list of op usernames."""
	ret = open(os.path.join(SERVER_DIR, 'ops.txt')).read().strip().split('\n')
	ret = [unicode(name) for name in ret]
	return ret

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
	if name not in color_map:
		raise ValueError('Bad color %s' % repr(name))
	return u'§' + color_map[name]


locks = set()
def tell(user, message, delay=0, lock=None):
	"""Send a server message to user.
	Optional args:
		delay: Wait delay seconds before sending message. Useful mainly with lock. See below.
		lock: Until message sent (see delay) allow no new messages with the same user and lock value.
			Generally speaking, expected to be a string. But it doesn't really matter.
	Returns bool of whether message was sent (see lock)
	"""
	global locks
	if lock is not None:
		if (user, lock) in locks:
			return False
		else:
			locks.add((user, lock))
	def tell_send():
		packet = Packet()
		packet.ident = packet_names['Chat message']
		packet.direction = CLIENT_TO_SERVER if to_server else SERVER_TO_CLIENT
		packet.data = {'text': unicode(message)}
		send_packet(packet, user, False)
		locks.remove((user, lock))

	if delay:
		schedule(tell_send, delay)
	else:
		tell_send()
