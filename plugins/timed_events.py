
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """A module for registering a callback to occur at a later time."""

def on_start():
	pass

def on_packet(packet, user, to_server):
	return packet

def on_tick():
	pass # TODO

def register(timeout, callback, key=None):
	"""Register a callback to occur after given timeout (int or float, seconds).
	If key is given, it will replace an old timeout (if any) with the same key.
	"""
	pass # TODO

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
