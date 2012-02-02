# -*- coding: cp1252 -*-
"""Helper functions for plugins"""

import os
from proxy import send_packet
from proxy import server_cmd as cmd
from config import *

def ops():
	"""Get list of op usernames."""
	ret = open(os.path.join(SERVER_DIR, 'ops.txt')).read().strip().split('\n')
	ret = [unicode(name) for name in ret]
	return ret

def color(name):
	"""Takes a color name and returns the string needed to turn the chat message that color."""
	color_map = {
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
	if name not in color_map:
		raise ValueError('Bad color %s' % repr(name))
	return u'§' + color_map[name]
