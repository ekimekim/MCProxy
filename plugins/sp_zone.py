from helpers import point_dist
from persistent_store import Store

new_zone_hooks = [] # Append to this list to register a function to call for new zones
# Function should take args (zone)

# bounds_info is a member of Zone, and encodes info on the bounds of the zone.
# Is a tuple (style, *args). Style is one of those listed in bounds_styles below.
# Args is dependent on style.

# Notes
#	Zones are dicts
#	If two zones overlap, you need permissions in BOTH to do the requested action.
#	For now, only priveliged users can make zones (potential for abuse)
#		Consider revising - propose and accept system?

def new_zone(name, bounds_info, creator):
	zone = {}
	zone['name'] = name
	zone['creator'] = creator
	zone['bounds_info'] = bounds_info
	for fn in new_zone_hooks:
		fn(zone)
	return zone


# --- bounds code ---

def bounds_cube(dim, a, b):
	ranges = zip(a,b) # Ranges is a list of (a_coord, b_coord)
	for axis in ranges:
		axis = sorted(axis)
	def cube_test(current_dim, point):
		return current_dim == dim and all(lower < coord < upper for coord, (lower, upper) in zip(point, ranges))
	return cube_test

def bounds_cyl(dim, base, radius, height)
	# base is the point at the bottom middle of the cyl
	base_x, base_y, base_z = base
	def cyl_test(current_dim, point)
		x, y, z = point
		return dim == current_dim and
			min_height <= y <= max_height and
			point_dist((x,z), (base_x, base_z)) <= radius
	return cyl_test

def bounds_union(*bounds_infos):
	def union_test(current_dim, point):
		return any(get_bounds_fn(*bounds_info)(current_dim, point) for bounds_info in bounds_infos)

bounds_styles = {'cube': bounds_cube, 'cylinder': bounds_cyl}

def get_bounds_fn(style, *args):
	fn = bounds_styles[style](*args)
	return fn

# --- End bounds code ---


def on_start():
	global zones
	zones = Store('zones') # This also loads up any old zones


def on_packet(packet, user, to_server):
	global zones

	#if dim change
	if not to_server and packet.name() in ("Login request", "Respawn"):
		user.dimension = packet.data["dimension"]
		
	#if movement
	if packet.name() in ('Player position', 'Player position & look', 'Spawn Position'):
		pos = (packet.data['x'], packet.data['y'], packet.data['z'])
		user.zones = [get_bounds_fn(*zone['bounds_info'])(user.dimension, pos) for zone in zones]

	return packet
