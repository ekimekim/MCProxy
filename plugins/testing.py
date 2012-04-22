
""" Only ever used for temp testing of features. """

import player_cmd as cmd
from zones import new_zone_hooks, new_zone, get_zones
from plugin_helpers import tell

def on_start():
	cmd.register('/testzone new ([^ ]+)', on_cmd)
	cmd.register('/testzone view', on_cmd2)
	re_name = r'(?:[^"][^ ]+|"(?:[^"]|\\")+")'
	cmd.register(r'/testacl (%s) ((?:add)|(?:rm)) ([^ ]+) ([^ ]+)' % re_name, on_cmd3)

def on_cmd(message, user, name):
	offset = user.position
	offset = [axis+5 for axis in offset]
	if new_zone(name, ('cube', user.dimension, user.position, offset), user.username):
		tell(user, "Success")
	else:
		tell(user, "Failure")

def on_cmd2(message, user):
	flag = False
	for zone in user.zones:
		flag = True
		tell(user, "In zone: %s%s" % (zone['name'], zone['acls']))
	if not flag:
		tell(user, "In no zones.")


def on_cmd3(message, user, zone, add_or_rm, username, rule):
	zone = zone.strip('"')
	try:
		acls = get_zones()[zone]['acls']
	except KeyError:
		tell(user, "No such zone")
		return
	user_acls = acls.setdefault(username, acls['EVERYONE'])
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
