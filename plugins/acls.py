
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """A plot-protection system based on the zones plugin.
Gives each zone a set of ACLs as follows:
	ENTRY - Allow players to move into the zone.
	INTERACT - Allow players to open doors, flip levers, etc.
	MODIFY - Allow players to create or destroy blocks in the zone.
	ADMIN - Allow players to modify the ACLs
Each control is a seperate field, however in practice most players will want
to give a control level plus all those above it, eg. MODIFY implies INTERACT, ENTRY.
It is suggested that all interfaces have this as default behaviour.
"""

import zones

# It is suggestd to use the symbolic names.
ENTRY = 'ENTRY'
INTERACT = 'INTRACT'
MODIFY = 'MODIFY'
ADMIN = 'ADMIN'

DEFAULTS = [ENTRY]
DEFAULT_ADMIN = [ENTRY, INTERACT, MODIFY, ADMIN]


def on_new_zone(zone):
	zone['acls'] = {
		'EVERYONE': DEFAULTS,
		zone['creator']: DEFAULT_ADMIN
	}


def on_start():
	zones.new_zone_hooks.append(on_new_zone)


