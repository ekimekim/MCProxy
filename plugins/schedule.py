
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """A module for registering a callback to occur at a later time."""

import time

events = [] # list of (time, key, callback), ordered on time.

def register(timeout, callback, key=None):
	"""Register a callback to occur after given timeout (int or float, seconds).
	If key is given, it will replace an old timeout (if any) with the same key.
	"""

	try:
		clear(key)
	except KeyError:
		pass

	new_time = time.time() + timeout
	for i in range(len(events)):
		event_time, event, event_key = events[i]
		if event_time > new_time:
			events.insert(i, (new_time, callback_fn, key))
			break
	else:
		events.append((new_time, callback_fn, key))


def check(key):
	"""Returns time remaining for timeout with given key.
	If no such timeout exists, raises KeyError.
	"""
	for event_time, event, event_key in events:
		if key == event_key:
			return event_time - time.time()
	raise KeyError(key)


def clear(key):
	"""Removes timeout with given key (returns time that remained).
	If no such timeout exists, raises KeyError.
	"""
	for i in range(len(events)):
		event_time, event, event_key = events[i]
		if key == event_key:
			events.pop(i)
			return event_time - time.time()
	raise KeyError(key)


def on_tick(users):
	now = time.time()
	while events and now >= events[0][0]:
		events[0][1]()
		events.pop(0)
