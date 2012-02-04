
AUTHOR="ekimekim (based on sleepyparadox's 'sp_opcolor')"
CONTACT='mikelang3000@gmail.com'
DESCRIPTION= """A plugin that highlights usernames in chat.
Has different colours for ops, logged in users, not logged in users, and yourself.
Colours have sensible defaults but are configurable with in-game commands:
	/colors help
	/colors TYPE COLOR
"""

from packet_decoder import Packet
from helpers import ops, color

opColor = color('red')
userColor = color('dark cyan')

def on_start():
	cmd.register('/color (.*)', on_command)

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

HELP = """Chat color commands:
/color help - This message
/color colors - List available colors
/color all X - set all chat messages to X
/color active X - set logged in usernames to X
/color inactive X - set logged out usernames to X
/color me X - set yourself to appear as X
___Note: Only you see the new color, not everyone.
/color ops X - set ops to appear as X
Replace X with the color you want, as given by /color colors."""

def on_command(message, user, command):
	verb, value = command.split(' ', 1)
	if verb == 'help':
		user.tell(HELP)
	elif verb in user.setcolors:
		if value in color.colors
