
""" Only ever used for temp testing of features. """

import player_cmd as cmd
from plugin_helpers import tell
from long_operations import long_operation
import time

def on_start():
	cmd.register('/test', on_cmd)

def on_cmd(message, user):
	tell(user, test(user))


@long_operation
def test(user):
	yield "Hello"
	while 1:
		tell(user, time.time())
		yield
