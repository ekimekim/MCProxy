
AUTHOR = "ekimekim"
CONTACT = "mikelang3000@gmail.com"
DESCRIPTION = """This, like helpers.py, is for helper functions.
However, it is reserved for functions that require other plugins to work.
This cannot be done from helpers.py.
Hence we have a helper plugin.
"""

import helpers
from schedule import schedule


locks = set()
def tell(user, message, delay=0, lock=None, prefix=''):
	"""Send a server message to user.
	Note: Splits multiline messages. See prefix, below.
	Optional args:
		delay: Wait delay seconds before sending message. Useful mainly with lock. See below.
		lock: Until message sent (see delay) allow no new messages with the same user and lock value.
			Generally speaking, expected to be a string. But it doesn't really matter.
		prefix: Add given prefix to every line sent, eg '<server>: '.
	Returns bool of whether message was sent (see lock).

	Note: Apart from delay and lock args, this function acts like helpers.tell()
	"""
	global locks
	if lock is not None:
		if (user, lock) in locks:
			return False
		else:
			locks.add((user, lock))
	message = unicode(message)
	def tell_send():
		helpers.tell(user, message, prefix=prefix)
		if lock is not None:
			locks.remove((user, lock))

	if delay:
		schedule(tell_send, delay)
	else:
		tell_send()
