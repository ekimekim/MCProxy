# -*- coding: cp1252 -*-

AUTHOR='sleepyparadox'
CONTACT='sleepyparadox@gmail.com'
DESCRIPTION= """Sleepy Paradox - Op Color
A simple plugin that highlights the developers efforts.
Highlights 'Sleepy Paradox' and ekimekim' in red.
Also replaces 'bitblitz' with 'Sleepy Paradox' (To make account consistent with developer name)"""

from packet_decoder import Packet
from helpers import send_packet
from helpers import ops

opColor = color('red')

def on_start():
    pass

def on_packet(packet, user, to_server):
    if packet.name() == 'Chat message':
        #Highlight admin names in red
        if not to_server:
            for op in ops():
                #insert op color flag before name and normal color flag after name
                packet.data['text'] = packet.data['text'].replace(op, opColor + op + color('white'))
                
            #replace 'bitblitz' with developer name 'Sleepy Paradox'
            packet.data['text'] = packet.data['text'].replace(u'bitblitz', u'Sleepy Paradox')
    #return edited packet
    return packet

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
	if color not in color_map:
		raise ValueError('Bad color')
	return u'§' + color_map[color]
