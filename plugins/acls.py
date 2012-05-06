
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """A plot-protection system based on the zones plugin.
Gives each zone a set of ACLs as follows:
	ENTRY - Allow players to move into the zone.
	INTERACT - Allow players to open doors, flip levers, etc. (ONLY IF HANDS EMPTY (techincal limitations))
	MODIFY - Allow players to create or destroy blocks in the zone.
	ADMIN - Allow players to modify the ACLs
Each control is a seperate field, however in practice most players will want
to give a control level plus all those above it, eg. MODIFY implies INTERACT, ENTRY.
It is suggested that all interfaces have this as default behaviour.

Note that if zones overlap (ie. player in more than one zone),
they need permissions in all zones.
"""

import zones
from packet_decoder import SERVER_TO_CLIENT, Packet
from helpers import send_packet
from plugin_helpers import tell

# It is suggestd to use the symbolic names.
ENTRY = 'ENTRY'
INTERACT = 'INTERACT'
MODIFY = 'MODIFY'
ADMIN = 'ADMIN'

DEFAULTS = [ENTRY]
DEFAULT_ADMIN = [ENTRY, INTERACT, MODIFY, ADMIN]
ALL_PERMS = [ENTRY, INTERACT, MODIFY, ADMIN]


# The following item ids are NOT block placements and may be used to interact.
INTERACT_IDS = [
	-1, 322, 345
]
# Ignoring the python hackery on the first line, this is a list of ranges [a,b] inclusive to add to INTERACT_IDS
INTERACT_IDS += sum([range(a,b+1) for a,b in [
	(256,258),
	(260,294),
	(296,320),
	(334,341),
	(347,353),
	(357,360),
	(363,378),
	(381,382),
	(384,385),
	(2256,2266)
]],[])


def on_new_zone(zone):
	zone['acls'] = {
		'EVERYONE': DEFAULTS,
		zone['creator']: DEFAULT_ADMIN
	}


def on_start():
	zones.new_zone_hooks.append(on_new_zone)


def get_acls(zone, user):
	return zone['acls'].get(user.username, zone['acls']['EVERYONE'])


def on_packet(packet, user, to_server):
	if not to_server:
		return packet

	# ENTRY
	if packet.name() in ('Player position', 'Player position & look') and not check_acls(ENTRY, user):
		tell(user, "You are not allowed to enter here.", delay=0.2, lock=("acl-entry-lock",user))
		new_stance = packet.data['stance'] - packet.data['y'] + user.position_old[1]
		packet.data['x'], packet.data['y'], packet.data['z'] = user.position_old
		packet.data['stance'] = new_stance
		back_packet = Packet()
		back_packet.ident = 0x0B # Player position
		back_packet.direction = SERVER_TO_CLIENT
		back_packet.data['x'] = packet.data['x']
		back_packet.data['y'] = packet.data['y']
		back_packet.data['z'] = packet.data['z']
		back_packet.data['stance'] = packet.data['stance']
		back_packet.data['on_ground'] = packet.data['on_ground']
		send_packet(back_packet, user, False)
		return packet

	# MODIFY (block digging)
	if packet.name() == 'Player digging' and packet.data['status'] == 0:
		position = (packet.data['x'], packet.data['y'], packet.data['z'])
		if not check_acls(MODIFY, user, position):
			tell(user, "You are not allowed to dig here.")
			return []

	# MODIFY/INTERACT (block placement)
	if packet.name() == 'Player block placement' and not all(packet.data[key] == -1 for key in ('x','y','z','direction')):
		position = add_direction((packet.data['x'], packet.data['y'], packet.data['z']), packet.data['direction'])
		if packet.data['slot']['id'] in INTERACT_IDS:
			if not check_acls(INTERACT, user, position):
				tell(user, "You are not allowed to interact with things here.")
				return []
		else:
			if not check_acls(MODIFY, user, position):
				tell(user, "You are not allowed to place blocks here.")

				# For now, we tell the client that the block in the indicated direction is empty.
				# This should work almost all the time and is by far the easiest option.
				back_packet = Packet()
				back_packet.ident = 0x35 # Block change
				back_packet.direction = SERVER_TO_CLIENT
				back_packet.data['x'], back_packet.data['y'], back_packet.data['z'] = position
				back_packet.data['id'] = 0
				back_packet.data['metadata'] = 0
				send_packet(back_packet, user, False)

				# We also invalidate the packet rather than drop it, so the server auto-corrects the client's inventory
				packet.data['x'] += 100

	return packet


def check_acls(permission, user, position=None):
	"""Return bool whether user may currently <permission> at <position:defaults to user's position>"""
	if hasattr(user, 'acl_force') and user.acl_force:
		return True
	if position is None:
		position = user.position
	for zone in zones.get_zones_at_point(user.dimension, position):
		if 'confirmed' in zone and zone['confirmed']:
			if permission not in get_acls(zone,user):
				return False
	return True


def add_direction(position, direction):
	"""Returns the position one block in the given direction. Direction is an int as per the minecraft packet protocol."""
	x, y, z = position
	if direction == 0:
		y -= 1
	elif direction == 1:
		y += 1
	elif direction == 2:
		z -= 1
	elif direction == 3:
		z += 1
	elif direction == 4:
		x -= 1
	elif direction == 5:
		x += 1
	else:
		raise ValueError("direction must be between 0 and 5 inclusive, got %s" % direction)
	return x, y, z
