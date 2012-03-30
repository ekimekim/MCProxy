
""" Only ever used for temp testing of features. """

import player_cmd as cmd
from zones import new_zone_hooks, new_zone
from plugin_helpers import tell

def on_start():
	cmd.register('/test', on_cmd)
	cmd.register('/test2', on_cmd2)
	new_zone_hooks.append(on_new_zone)

n = 0
def on_cmd(message, user):
	global n
	n += 1
	if new_zone('test%d' % n, ('cylinder', user.dimension, user.position, 8, 16), user.username):
		tell(user, "Success")
	else:
		tell(user, "Failure")

def on_cmd2(message, user):
	for zone in user.zones:
		tell(user, "In zone: %s(%s)" % (zone['name'], zone.get('test','fail')))

def on_new_zone(zone):
	zone['test'] = 'blah'
