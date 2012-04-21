
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

def on_start():
	register("/acls help", aclhelp)
	register("/acls commands", aclcmdhelp)
#	register("/acls set ([^ ]+)((?: [A-Z]+)+)", aclset)
#	register("/acls add ([^ ]+) ([A-Z]+)", acladd)
#	register("/acls remove ([^ ]+) ([A-Z]+)", aclrm)
#	register("/acls clear ([^ ]+)", aclclear)


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
	tell(user, "Sorry, these commands aren't implemented yet. For now, your zones will default to "
	           "allowing you full access and everyone else ENTRY only. They should be done by tomorrow.")

#def aclset(message, user, name, ):
#def acladd(message, user):
#def aclrm(message, user):
#def aclclear(message, user):
