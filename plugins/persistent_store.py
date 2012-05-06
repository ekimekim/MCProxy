
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """A persistent data store for plugins.
Initialise your persistent object with Store(name, default).
name must be unique and identifies your object on disk.
default is the value to take if it does not exist on disk.
All values must be JSONable. That means strings, ints, floats, bools,
lists, tuples, dicts.
No action is required to save data. Data is synced every tick.
If you require a stronger guarentee, you can call sync() to force a sync early.
The top-level object itself must be either a list or a dict.
"""

import json, os, logging

from config import SERVER_DIR, DEBUG

data = {}

if not DEBUG:
	JSON_FILE = os.path.join(SERVER_DIR, 'persistent_data.json')
	JSON_FILE_TEMP = os.path.join(SERVER_DIR, '.persistent_data.json.tmp')
	JSON_FILE_BACKUP = os.path.join(SERVER_DIR, '.persistent_data.json~')
else:
	JSON_FILE = os.path.join(SERVER_DIR, 'persistent_data.debug.json')
	JSON_FILE_TEMP = os.path.join(SERVER_DIR, '.persistent_data.debug.json.tmp')
	JSON_FILE_BACKUP = os.path.join(SERVER_DIR, '.persistent_data.debug.json~')


class Store():
	_key = None
	def __init__(self, _key, default):
		global data
		if type(default) not in (list, tuple, dict):
			raise ValueError("Default value must be list, tuple or dict")
		self.__dict__['_key'] = _key
		if _key not in data:
			data[_key] = default
	def __getattr__(self, attr):
		global data
		return getattr(data[self._key], attr)
	def __getitem__(self, item):
		return data[self._key][item]
	def __setattr__(self, attr, value):
		setattr(data[self._key], attr, value)
	def __setitem__(self, item, value):
		data[self._key][item] = value


def on_start():
	global data
	data = json.load(open(JSON_FILE, 'rU'))
	if type(data) != dict:
		raise ValueError("Bad data in json store")


def on_packet(packet, user, to_server):
	return packet


def on_tick(users):
	sync()


def sync():
	global data
	try:
		os.rename(JSON_FILE, JSON_FILE_BACKUP)
		json.dump(data, open(JSON_FILE_TEMP, 'w'), indent=4)
		os.rename(JSON_FILE_TEMP, JSON_FILE)
	except:
		logging.warning("Using backup persistant store file")
		os.rename(JSON_FILE_BACKUP, JSON_FILE)
		raise
