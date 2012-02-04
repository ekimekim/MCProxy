
AUTHOR='sleepyparadox'
CONTACT='sleepyparadox@gmail.com'
DESCRIPTION= """Sleepy Paradox - Op Color
A simple plugin that highlights the developers efforts.
Highlights 'Sleepy Paradox' and ekimekim' in red.
Also replaces 'bitblitz' with 'Sleepy Paradox' (To make account consistent with developer name)"""

from packet_decoder import Packet
from helpers import ops, color

opColor = color('red')
userColor = color('dark cyan')

def on_start():
    pass

def on_packet(packet, user, to_server):
    if packet.name() == 'Chat message':
        #Highlight admin names in red
        if not to_server:
            for op in ops():
                #insert op color flag before name and normal color flag after name
                packet.data['text'] = packet.data['text'].replace(op, opColor + op + color('white'))
            packet.data['text'] = packet.data['text'].replace(user.username, userColor + user.username + color('white'))
                
            #replace 'bitblitz' with developer name 'Sleepy Paradox'
            packet.data['text'] = packet.data['text'].replace(u'bitblitz', u'Sleepy Paradox')
    #return edited packet
    return packet
