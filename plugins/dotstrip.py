
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """A simple plugin that changes players view if chat messages
beginning with a . as this generally is used as a way to escape meaning when telling others
how to do something.
eg. "./help" becomes "/help"
Should go BEFORE usercolours as it matches against beginning of string
"""

import re

def on_start():
	global match
	match = re.compile(r'^(<[a-zA-Z_]>) \./(.*)').match

def on_packet(packet, user, to_server):
	if packet.name() == 'Chat message':
		if match(packet.data['text']):
			packet.data['text'] = "%s /%s" % match.groups()
	return packet
