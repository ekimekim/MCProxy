
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
		'black': '0',
		'dark blue': '1',
		'dark green': '2',
		'dark cyan': '3',
		'dark red': '4',
		'purple': '5',
		'gold': '6',
		'gray': '7',
		'dark gray': '8',
		'blue': '9',
		'green': 'a',
		'cyan': 'b',
		'red': 'c',
		'pink': 'd',
		'yellow': 'e',
		'white': 'f'
	}
	if color not in color_map:
		raise ValueError('Bad color')
	return '§' + color_map[color]
