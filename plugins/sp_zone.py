from helpers import point_dist

# Format for a zone
# zone := (name, acls, tags, bounds_info)
# acls := {username:[acl_record], ...}
#	Special username "<everyone>" applies to any unlisted username
# acl_record := subset of ['enter', 'interact', 'modify', 'creative', 'admin'] - meanings:
#	'enter': Player may walk into zone
#	'interact': Player may interact with objects (levers, buttons, etc)
#	'modify': Player may place/destroy blocks
#	'creative': On creative server, player may use creative mode
#	'admin': Player may modify zone properties
# bounds_info := (style, *args)
#	style is str


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
		return any(check_bounds(*bounds_info)(current_dim, point) for bounds_info in bounds_infos)

bounds_styles = {'cube': bounds_cube, 'cylinder': bounds_cyl}

def check_bounds(style, *args):
	fn = bounds_styles[style](*args)
	return fn


def on_start():
	global aZones
	aZones = []
	aZones.append( CreateZoneCube("Wolf's Run", Vec3(92, 0, -53), Vec3(-43, 256, -216)))
	#aZones[0].aTags = [u"City"]
	aZones.append( CreateZoneCube("Pants", Vec3(100,0,100), Vec3(-100,256,-100)))
	#aZones[1].aTags = [u"NoBuild"]
	SaveZones()
	
	
def on_packet(packet, user, to_server):
	global aZones

	#if dim change
	if packet.name() == "Login request" and not to_server:
		user.dimension = GetDimensionName(packet.data["dimension"])
		print user.dimension
	if packet.name() == "Respawn":
		user.dimension = GetDimensionName(packet.data["dimension"])
		print user.dimension
		
	#if movement
	if packet.name() == 'Player position' or packet.name() == 'Player position & look':
		#clear zones
		user.aZones = []
		v3Pos = Vec3(packet.data['x'], packet.data['y'], packet.data['z'])
		#check which zones players are in
		for zone in aZones:
			if zone.PointInZone(v3Pos):
				#add zone
				user.aZones.append(zone)
		#print all zones to console
	   # print user.Zones
		#for zone in user.aZones:
			#print zone.szName
   
	return packet

