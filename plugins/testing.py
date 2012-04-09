
""" Only ever used for temp testing of features. """

import player_cmd as cmd
from zones import new_zone_hooks, new_zone, get_zones
from plugin_helpers import tell

def on_start():
	cmd.register('/test', on_cmd)
	cmd.register('/test', on_cmd)
	cmd.register(r'/testacl ([^ ]+) ((?:add)|(?:rm)) ([^ ]+) ([^ ]+)', on_cmd3)

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
		tell(user, "In zone: %s%s" % (zone['name'],zone['acls']))


def on_cmd3(message, user, zone, add_or_rm, username, rule):
	try:
		acls = get_zones()[zone]['acls']
	except KeyError:
		tell(user, "No such zone")
		return
	user_acls = acls.get(username, acls['EVERYONE'])
	if add_or_rm == 'add':
		if rule not in user_acls:
			user_acls.append(rule)
	elif add_or_rm == 'rm':
		try:
			user_acls.remove(rule)
		except ValueError:
			tell(user, "Rule not in list")
			return
	else:
		assert False

	tell(user, 'Success')
	return
