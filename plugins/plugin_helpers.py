
AUTHOR = "ekimekim"
CONTACT = "mikelang3000@gmail.com"
DESCRIPTION = """This, like helpers.py, is for helper functions.
However, it is reserved for functions that require other plugins to work.
This cannot be done from helpers.py.
Hence we have a helper plugin.
"""

import helpers
import schedule


def tell(user, message, delay=0, lock=None, prefix=''):
	"""Send a server message to user.
	Note: Splits multiline messages. See prefix, below.
	Optional args:
		delay: Wait delay seconds before sending message. Useful mainly with lock. See below.
		lock: Until message sent (see delay) allow no new messages with the same user and lock value.
			Generally speaking, expected to be a string. But it doesn't really matter.
			A common usage is a tuple ("namespace",user) for a per-user lock.
		prefix: Add given prefix to every line sent, eg '<server>: '.
	Returns bool of whether message was sent (see lock).

	Note: Apart from delay and lock args, this function acts like helpers.tell()
	"""
	message = unicode(message)
	tell_fn = lambda: helpers.tell(user, message, prefix=prefix)

	if delay:
		try:
			schedule.check(lock)
		except KeyError:
			schedule.register(delay, tell_fn, key=lock)
		else:
			return False
	else:
		tell_fn()

	return True


def ops_only(fn):
	"""Decorate a player_cmd callback to make it only match if user is op"""
	def wrapped_fn(message, user, *args):
		if user.username not in helpers.ops():
			return False
		else:
			return fn(message, user, *args)
	return wrapped_fn
