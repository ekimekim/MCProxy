
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """A module for registering a callback to occur at a later time."""


events = [] # ordered list of (time, key, callback)
#TODO UPTO

def register(timeout, callback, key=None):
	"""Register a callback to occur after given timeout (int or float, seconds).
	If key is given, it will replace an old timeout (if any) with the same key.
	"""
	new_time = time.time() + delay
	for i in range(len(events)):
		event_time, event = events[i]
		if event_time > new_time:
			events.insert(i, (new_time, callback_fn))
			break
	else:
		events.append((new_time, callback_fn))



def check(key):
	"""Returns time remaining for timeout with given key.
	If no such timeout exists, raises KeyError.
	"""
	pass # TODO

def clear(key):
	"""Removes timeout with given key.
	If no such timeout exists, raises KeyError.
	"""
	pass # TODO

def schedule(delay, callback_fn):
	"""Schedule callback_fn to run after (at least) delay seconds."""

def on_tick(users):
	now = time.time()
	while events and now >= events[0][0]:
		events[0][1]()
		events.pop(0)
