
AUTHOR = "ekimekim"
CONTACT = "mikelang3000@gmail.com"
DESCRIPTION = """Commands for controlling the acls of a zone:
	/acls help
	/acls set ZONE USER {PERMS}
	/acls add ZONE USER PERM
	/acls remove ZONE USER PERM
	/acls clear ZONE USER
"""

from player_cmd import register
from plugin_helpers import tell
from helpers import all_users, ops
from zones import get_zones
from acls import ALL_PERMS, ADMIN


def on_start():
	re_name = r'(?:[^"][^ ]+|"(?:[^"]|\\")+")'
	register("/acls help", aclhelp)
	register("/acls commands", aclcmdhelp)
	register("/acls (%s) set ([^ ]+)((?: [A-Z]+)+)" % re_name, aclset)
	register("/acls (%s) add ([^ ]+) ([A-Z]+)" % re_name, acladd)
	register("/acls (%s) remove ([^ ]+) ([A-Z]+)" % re_name, aclrm)
	register("/acls (%s) clear ([^ ]+)" % re_name, aclclear)


def aclhelp(message, user):
	tell(user, "ACLs are my equivilent of plot protection.\n"
	           "A zone (see /zone help) has permissions for different "
	           "users to do different things. The creator of a zone can change these. "
	           "The permissions available are:\n"
	           "ENTRY - Without this permission, you can't enter the zone.\n"
	           "INTERACT - Without this permission, you can't flip levers, open doors, etc. "
	           "Note: even with this permission, you need to not be holding a block in your hands for it to work.\n"
	           "MODIFY - Without this permission, you can't place or dig blocks.\n"
	           "ADMIN - This permission allows you to change the permissions of this zone.\n"
	           "Type /acls commands for help on how to modify permissions.")


def aclcmdhelp(message, user):
	tell(user, "ACL commands:\n"
	           "/acls <zone> set <user> <permissions>\n"
	           "__ Set the user's permissions in that zone to exactly\n"
	           "__ the permissions given. Permissions should be\n"
	           "__ space-seperated, eg. ENTRY INTERACT MODIFY\n"
	           "/acls <zone> add <user> <permission>\n"
	           "__ Add a single permission to what a user can do.\n"
	           "/acls <zone> remove <user> <permission>\n"
	           "__ Remove a single permission from what a user can do.\n"
	           "/acls <zone> clear <user>\n"
	           "__ Reset the given user to use the default permissions.\n"
	           "To modify the default permissions, replace <user> with EVERYONE.")


def common(fn):
	"""Wrap funciton. Get zone based on name and .lower usernames."""
	def wrapped_fn(message, user, zone, name, *args):

		zone_original = zone
		zone = zone.strip('"')
		if zone not in get_zones():
			tell(user, "Zone does not exist.")
			print zone
			return
		zone = get_zones()[zone]
		if 'acls' not in zone:
			tell(user, "Sorry, that zone does not appear to support ACLs.\n"
			           "You may need to contact an op to resolve this.")
			return

		if name != 'EVERYONE':
			name = name.lower()
			if name not in all_users() and name not in zone['acls']:
				tell(user, "Warning: %s is not a player known to this server.\n"
				           "If you have made a mistake, type:\n/acls %s clear %s" % (zone_original, name))

		if ADMIN not in zone['acls'].get(user.username, zone['acls']['EVERYONE']) and user.username not in ops():
			tell(user, "You do not have permission to modify ACLs for this zone. "
			           "If you have accidentially locked yourself out, please contact an op for assistance.")
			return

		return fn(message, user, zone, name, *args)
	return wrapped_fn


@common
def aclset(message, user, zone, name, perms):
	perms = filter(None, perms.split())
	for perm in perms:
		if perm not in ALL_PERMS:
			tell(user, "%s not an ACL." % perm)
			return
	zone['acls'][name] = perms
	tell(user, "Success")


@common
def acladd(message, user, zone, name, perm):
	if perm not in ALL_PERMS:
		tell(user, "%s not an ACL." % perm)
	current = zone['acls'].setdefault(name, zone['acls']['EVERYONE'][:])
	if perm in current:
		tell(user, "%s can already %s" % (name, perm))
	else:
		current.append(perm)
		tell(user, "Success")


@common
def aclrm(message, user, zone, name, perm):
	if perm not in ALL_PERMS:
		tell(user, "%s not an ACL." % perm)
	current = zone['acls'].setdefault(name, zone['acls']['EVERYONE'][:])
	if perm not in current:
		tell(user, "%s already can't %s" % (name, perm))
	else:
		current.remove(perm)
		tell(user, "Success")


@common
def aclclear(message, user, zone, name):
	if name not in zone['acls']:
		tell(user, "%s doesn't have any specific ACLs" % name)
	else:
		zone['acls'].pop(name)
		tell(user, "Success")
