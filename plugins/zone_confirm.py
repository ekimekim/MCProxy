
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """Newly created zones must be submitted for op approval.
Ops gain commands:
	/zone op help
	/zone op wool ZONE - Paint 10x10x10 area about and below op in green woll for requested zone, red wool other zone, yellow if both.
	/zone op confirm ZONE
"""

import zones
from player_cmd import register
from helpers import ops
from plugin_helpers import tell

def set_confirm(zone):
	zone['confirmed'] = False

def on_start():
	zones.new_zone_hooks.append(set_confirm)
	register("/zone op help", ophelp)
	register("/zone op wool (.*)", zonewool)
	register("/zone op confirm (.*)", zoneconfirm)

def ops_only(fn):
	def wrapped_fn(message, user, *args):
		if user.username not in ops():
			return False
		else:
			return fn(message, user, *args)
	return wrapped_fn

@ops_only
def ophelp(message, user):
	tell(user, "Note that unlike /zone commands, zone names are taken verbatim (no quotes).\n"
	           "/zone op help - Obvious.\n"
	           "/zone op wool <zone> - 10x10x10 cube below player highlighted as follows:\n"
	           "__ green: In given zone.\n"
	           "__ red: In zone besides one given.\n"
	           "__ yellow: In given zone AND at least one other.\n"
	           "__ You will need to log out/in to reverse changes.\n"
	           "/zone op confirm <zone> - Confirm zone.")


@ops_only
def zoneconfirm(message, user, name):
	if name not in zones.get_zones():
		tell(user, "Zone does not exist.")
		return
	zones.get_zones()[name]['confirmed'] = True
	tell(user, "Success")


@ops_only
def zonewool(message, user, name):
	pass # TODO