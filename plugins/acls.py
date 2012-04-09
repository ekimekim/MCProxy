
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

Note that if zones overlap (ie. player in more than one zone),
they need permissions in all zones.
"""

import zones
from packet_decoder import SERVER_TO_CLIENT

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


def on_packet(packet, user, to_server):
	if not to_server:
		return packet

	# ENTRY
	if packet.name() in ('Player position', 'Player position & look', 'Spawn Position'):
		if any(ENTRY not in zone for zone in user.zones):
			packet.data['x'], packet.data['y'], packet.data['z'] = user.position_old
			back_packet = packet.copy()
			back_packet.direction = SERVER_TO_CLIENT
			send_packet(back_packet, user, False)
			return packet
		else:
			return packet

	# INTERACT TODO
	#elif packet.name() in ():

	# MODIFY (block digging)
	elif packet.name() in ('Player digging') and packet.data['status'] == 0:
		return []

	# MODIFY (block placement) TODO
	#elif packet.name() in ():

	else:
		return packet
