
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """This module is a unified system for presenting the user with a list of choices.
It's primarily intended to implement menus.
Some useful notes:
	A player only has one active menu at once. Only that menu's callback can remove/change it.
	Any other calls to open a menu will raise MenuLockError
	Menus are session-specific. No indication will be given if player logs out.
Players interact with menus in the following way:
	Once the options have been presented, the player is asked to make a choice.
	A timeout may be given on this choice.
	The player may type ":1", ":2", etc to make a choice.
	They may also type ":again" to get the text resent,
		or ":exit" to leave the menu.
Finally, an extra functionality offered is a prompt menu,
	this acts like a menu but asks the player a question, which they answer with ":<answer>".
"""

DEFAULT_TIMEOUT = 60

import player_cmds as cmds
import timed_events
from helpers import tell


MENU_HELP = """TODO
"""


class MenuLockError(StandardError):
	def __init__(self, user, menu):
		self.user = user
		self.menu = menu
	def __str__(self):
		return "%s is currently in menu %s" % (self.user, self.menu)


def on_start():
	cmds.register(":(.*)", on_cmd)
	cmds.register("/menus", lambda msg, user: tell(user, MENU_HELP))


def on_packet(packet, user, to_server):
	return packet


def display(user, menu_text, options, exit_callback, timeout=None):
	"""Display given menu to player. Menu format is as follows:
		menu_text: The main "body" text of the menu
		options: A list of tuples ("option text", option_callback). option_callback is called if the option is picked.
			Alternately, setting options=('prompt', callback) asks the user for a string instead. Note the string 'exit' is impossible.
		exit_callback: Called if the player tries to exit the menu.
		timeout: Optional. Either a timeout in (float,int) seconds, or a tuple (timeout, callback),
			where the callback is called after timeout. Else the exit_callback is called.
			If not given, has a default timeout menus.DEFAULT_TIMEOUT

		Callback functions act as follows:
			Should take args (user, response)
				Response will generally be the number they picked to pick the given callback option,
				but will be 'exit' for the exit_callback, None if it timed out, or the full response if 'prompt' was given.
			Should return either None (player no longer in a menu),
				or a tuple (menu_text, options, exit_callback, timeout) as per this function's args.
				Note that timeout is still optional.

		If another menu is currently active, raises a menus.MenuLockError
	"""

	if hasattr(user, 'menu') and user.menu is not None:
		raise menus.MenuLockError(user, user.menu)

	if timeout is None:
		timeout = DEFAULT_TIMEOUT
	if type(timeout) is not tuple:
		timeout = (timeout, exit_callback)

	user.menu = (menu_text, options, exit_callback, timeout)
	tell(user, menu_text)
	n = 0
	if len(options) and options[0] == 'prompt':
		tell(user, "Please enter :your response")
	else:
		for option, callback in options:
			n += 1
			tell(user, ":%d  %s" % (n, option))
	tell(user, "")

	timed_events.register(timeout[0], lambda: on_timeout(user), key=('menu', user))


def on_cmd(full_message, user, value):
	if (not hasattr(user, 'menu')) or user.menu is None:
		return False # Let cmd pass through
	
	menu_text, options, exit_callback, timeout = user.menu

	if value == 'exit':
		callback = exit_callback
	elif len(options) and options[0] == 'prompt':
		callback = options[1]
	else:
		try:
			n = int(value)
		except ValueError:
			tell(user, "Not a number: %s" % value)
			return True
		if not 0 < n <= len(options):
			tell(user, "%d not a valid option" % n)
			return True
		callback = options[n][1]

	new_menu = callback(user, value)
	user.menu = None
	timed_events.clear(('menu', user))
	if new_menu is not None:
		display(user, *new_menu)

	return True


def on_timeout(user):
	menu_text, options, exit_callback, timeout = user.menu
	new_menu = callback(user, value)
	user.menu = None
	if new_menu is not None:
		display(user, *new_menu)
