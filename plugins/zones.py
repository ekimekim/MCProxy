from helpers import point_dist
from persistent_store import Store

# TODO documentation

new_zone_hooks = [] # Append to this list to register a function to call when a new zone is made.
# Function should take args (zone) and, by convention, should store any data it needs to in the Zone object itself,
# ie. other plugins should not be maintaining auxillary data stores.
# In addition, the function may return False to reject the zone, True or None to accept it.

# bounds_info is a member of Zone, and encodes info on the bounds of the zone.
# Is a tuple (style, *args). Style is one of those listed in bounds_styles below.
# Args is dependent on style.

# Notes
#	Zones are dicts
#	If two zones overlap, you need permissions in BOTH to do the requested action.
#	For now, only priveliged users can make zones (potential for abuse)
#		Consider revising - propose and accept system?

# Example Zone
# {
#	'name': 'Example Zone',
#	'creator': 'Player',
#	'bounds_info': ('union',
#		('cube', 0, (-64,0,-64), (64,256,64)),
#		('cylinder', -1, (0,0,0), 8, 256))
#	'something_random': "Hey, I placed this message from a different plugin using a new zone hook"
# }
# Note the area the zone covers: In the overworld, a cube covering the 128x128 square about (0,0) (full height)
#                                In the nether, a cylinder covering a 8-radus area about (0,0) (full height)

def new_zone(name, bounds_info, creator):
	"""Create a new zone and call hooks. On success, returns new zone. Else returns None."""
	global zones
	zone = {}
	zone['name'] = name
	zone['creator'] = creator
	zone['bounds_info'] = bounds_info
	for fn in new_zone_hooks:
		ret = fn(zone)
		if ret is not None and not ret:
			break
	else:
		zones.append(zone)
		return zone
	return None


# --- bounds code - these functions generate "is point within" functions ---

def bounds_cube(dim, a, b):
	ranges = zip(a,b) # Ranges is a list of (a_coord, b_coord)
	for axis in ranges:
		axis = sorted(axis)
	def cube_test(current_dim, point):
		return current_dim == dim and all(lower < coord < upper for coord, (lower, upper) in zip(point, ranges))
	return cube_test

def bounds_cyl(dim, base, radius, height):
	"""base is the point at the bottom middle of the cyl"""
	base_x, base_y, base_z = base
	def cyl_test(current_dim, point):
		x, y, z = point
		return dim == current_dim and \
			base_y <= y <= base_y + height and \
			point_dist((x,z), (base_x, base_z)) <= radius
	return cyl_test

def bounds_union(*bounds_infos):
	def union_test(current_dim, point):
		return any(get_bounds_fn(*bounds_info)(current_dim, point) for bounds_info in bounds_infos)

bounds_styles = {'cube': bounds_cube, 'cylinder': bounds_cyl, 'union': bounds_union}

def get_bounds_fn(style, *args):
	fn = bounds_styles[style](*args)
	return fn

# --- End bounds code ---

def get_zones():
	# This function is some python magic that prevents issues with import order. Use it instead of accessing zones directly.
	global zones
	return zones


def on_start():
	global zones
	zones = Store('zones', []) # This also loads up any old zones


def on_packet(packet, user, to_server):
	global zones

	#if dim change
	if not to_server and packet.name() in ("Login request", "Respawn"):
		user.dimension_old = user.dimension
		user.dimension = packet.data["dimension"]
	#if movement
	elif packet.name() in ('Player position', 'Player position & look', 'Spawn Position'):
		pos = (packet.data['x'], packet.data['y'], packet.data['z'])
		user.position_old = user.position
		user.position = pos
	else:
		return packet

	user.zones_old = user.zones
	user.zones = (zone for zone in zones if get_bounds_fn(*zone['bounds_info'])(user.dimension, user.position)) # Note the lazy eval :D

	return packet
