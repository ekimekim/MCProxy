
AUTHOR="ekimekim (based on sleepyparadox's 'sp_opcolor')"
CONTACT='mikelang3000@gmail.com'
DESCRIPTION= """A plugin that highlights usernames in chat.
Has different colours for ops, logged in users, not logged in users, and yourself.
Colours have sensible defaults but are configurable with in-game commands:
	/colors help
	/colors TYPE COLOR
"""

from packet_decoder import Packet
from helpers import ops, color, colors, all_users, active_users, tell
import player_cmd as cmd

defaults = {
	'all': color('white'),
	'inactive': color('dark gray'),
	'active': color('gray'),
	'ops': color('red'),
	'me': color('dark cyan')
}

users = {}

def on_start():
	cmd.register('/color (.*)', on_command)
	cmd.register('/color ?', no_command)

def on_packet(packet, user_obj, to_server):
	if packet.name() == 'Chat message' and not to_server:
		prefs = users.get(user_obj.username, defaults)
		offlines = dict([(user, prefs['inactive']) for user in all_users()])
		onlines = dict([(user, prefs['active']) for user in active_users()])
		ops_dict = dict([(user, prefs['ops']) for user in ops()])
		player = {user_obj.username: prefs['me']}
		names = {}
		names.update(offlines)
		names.update(onlines)
		names.update(ops_dict)
		names.update(player)
		packet.data['text'] = prefs['all'] + packet.data['text']
		for name in names:
			packet.data['text'] = packet.data['text'].replace(name, names[name] + name + prefs['all'])
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
	parts = command.split(' ', 1)
	if len(parts) == 2:
		verb, value = parts
	else:
		verb = parts[0]
	if verb == 'help':
		tell(user, HELP)
	elif verb == 'colors':
		for c in colors:
			prefs = users.get(user.username, defaults)
			tell(user, 'color: %s"%s"%s' % (color(c), c, prefs['all']))
	elif verb in defaults:
		if value in colors:
			prefs = users.get(user.username, defaults.copy())
			prefs[verb] = color(value)
			users[user.username] = prefs
		else:
			tell(user, 'color: That is not a valid color!')
	else:
		tell(user, 'color: Bad command. Try "/color help"')


def no_command(message, user):
	tell(user, 'Modify user colors! Type "/color help".')
