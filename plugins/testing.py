
""" Only ever used for temp testing of features. """

import schedule
import player_cmd as cmd
from plugin_helpers import tell

def on_start():
	cmd.register('/test', on_cmd)

def on_cmd(message, user):
	tell(user, "First message")
	tell(user, "Third message", delay=5, lock="test message")
	tell(user, "Second message", delay=3)
	tell(user, "Bad message", delay=1, lock="test message")
