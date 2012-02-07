
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """A module intended to be a single module for command-like chat triggers.
Modules shoud register a regex to match a chat message exactly.
Along with this regex is a callback function that has args: (message, user, *regex_groups)
	and returns False to let packet pass through or True to drop it.
	If None is returned, defaults to dropping it.
This behaviour is intended to allow further checking before deciding if the packet should be dropped.
Messages are passed through all matching functions (unless dropped)
	in the order of regsitration (shich should occur during on_start()).
"""

import re

registrations = [] # List of (regex obj, function)


def on_start():
	pass


def on_packet(packet, user, to_server):
	global registrations

	if not to_server or packet.name() != 'Chat message':
		return packet

	message = packet.data['text']

	for regex, func in registrations:
		match = regex.match(message)
		if match is not None:
			ret = func(message, user, *match.groups())
			if ret is None or ret:
				break # break skips the else and so returns [] immediately
	else: # runs only if break is never reached, ie. no dropping matches.
		return packet
	return []


def register(regex, func):
	"""Register a callback function to be called when a chat message matches regex.
	regex should be a valid regular expression that matches against the whole chat message.
	func should take args (message, user, *regex_groups) and return False
		to pass packet along or True to drop it.
		regex_groups are the groups returned by a regex match (as per re.match(regex).groups)
	Example:
		def private_msg(message, user, target, priv_msg):
			# sends target the message priv_msg
			return True # drop packet

		def on_start():
			cmd.register('/msg ([^ ]+) (.*)', private_msg)
	"""
	global registrations
	regex = r'(?:%s)$' % regex # Make match end of string also
	regex = re.compile(regex)
	registrations.append((regex, func))
