
AUTHOR = "ekimekim"
CONTACT = "mikelang3000@gmail.com"
DESCRIPTION = """Some simple commands for using the zone stuff:
	/zone view - show all zones you have admin rights to
	/zone view NAME - show a specific zone that you have admin rights to and attributes
	/zone here - show what zones you're currently in, and what you may do.
	/zone new NAME ARGS - advanced zone create tool
	/zone destroy NAME - destroy a zone
	/zone help - list of commands
	/zone help COMMAND - usage on one command
Note on names:
	Names may contain whitespace but if so must be enclosed in "double quotes".
	If a name contains a double quote (seriously people...) it must be escaped with a backslash.
"""

from player_cmd import register
from plugin_helpers import tell
from helpers import ops
from zones import get_zones, new_zone
from json import loads

try:
	from acls import ADMIN
except ImportError:
	ADMIN = None


def on_start():
	re_name = r'(?:[^"][^ ]+|"(?:[^"]|\\")+")'
	register("/zone view", zonelist)
	register("/zone view (%s)" % re_name, zoneinfo)
	register("/zone here", zonehere)
	register("/zone new (%s) (.*)" % re_name, zonenew)
	register("/zone destroy (%s)" % re_name, zonedestroy)
	register("/zone help", helplist)
	register("/zone help ([^ ]+)", helpinfo)


def controls_zone(username, zone):
	if 'acls' in zone:
		return ADMIN in zone['acls'].get(username, zone['acls']['EVERYONE'])
	else:
		return username == zone['creator']


def zonelist(message, user):
	for zone in get_zones().values():
		if controls_zone(user.username, zone):
			tell(user, zone['name'] + (" (unconfirmed)" if not zone.get('confirmed',True) else ""))


def zonehere(message, user):
	flag = False
	for zone in user.zones:
		if 'acls' in zone:
			perms = zone['acls'].get(user.username, zone['acls']['EVERYONE'])
			perms = ": " + " ".join(perms)
		else:
			perms = ""
		tell(user, zone['name'] + perms)
		flag = True
	if not flag:
		tell(user, "In no zones.")


def zoneinfo(message, user, name):
	name = name.strip('"')

	try:
		zone = get_zones()[name]
	except KeyError:
		tell(user, "That zone doesn't exist!")
		return
	if not controls_zone(user.username, zone) and not user.username in ops():
		tell(user, "That isn't your zone.")
		return

	keys = ['name','creator','confirmed']
	for key in keys:
		if key in zone:
			tell(user, "%s: %s" % (key, zone[key]))

	keys.append('bounds_info')
	def dim_to_name(dim):
		try:
			return {-1: '(Nether)', 0: '(Overworld)', 1:'(End)'}[dim]
		except KeyError:
			return ""
	def tell_bounds(style, *args, **kwargs):
		indent = kwargs.pop("indent",0)
		indent_str = "__" * indent
		if style == 'cube':
			dim, point1, point2 = args
			tell(user, indent_str + "Cube in dim%d%s from (%.2f,%.2f,%.2f) to (%.2f,%.2f,%.2f)" % ((dim, dim_to_name(dim)) + tuple(point1) + tuple(point2)))
		elif style == 'cylinder':
			dim, base, radius, height = args
			tell(user, indent_str + "Cylinder in dim%d%s from (%.2f,%.2f,%.2f) to radius %.2f and height %.2f" % ((dim, dim_to_name(dim)) + tuple(base) + (radius, height)))
		elif style == 'union':
			tell(user, indent_str + "Union of regions:")
			for more_info in args:
				tell_bounds(*more_info, indent=indent+1)
		else:
			tell(user, indent_str + "Unknown region")
	tell_bounds(*zone['bounds_info'])

	if 'acls' in zone:
		keys.append('acls')
		tell(user, "acls:")
		for name in zone['acls']:
			if name == 'EVERYONE':
				continue
			tell(user, "__%s: %s" % (name, ",".join(zone['acls'][name])))
		tell(user, "__Everyone else: %s" % ",".join(zone['acls']['EVERYONE']))

	for key in zone:
		if key in keys:
			continue
		tell(user, "%s: %s" % (key, zone[key]))


def zonenew(message, user, name, args):
	name = name.strip('"')

	if name in get_zones():
		tell(user, "Name already taken.")
		return

	if args.startswith("json "):
		try:
			data = loads(args[5:])
		except Exception:
			tell(user, "Bad json.")
			return

		def validate_point(data):
			if type(data) != list:
				raise ValueError()
			if len(data) != 3:
				raise ValueError()
			if not all(type(x) in (int, float) for x in data):
				raise ValueError()

		def validate_info(data):
			if type(data) != list:
				raise ValueError()
			style = data[0]
			if style == 'cube':
				dim, point1, point2 = data[1:]
				if type(dim) != int or dim not in (-1,0,1):
					raise ValueError()
				validate_point(point1)
				validate_point(point2)
			elif style == 'cylinder':
				dim, base, radius, height = data[1:]
				if type(dim) != int or dim not in (-1,0,1):
					raise ValueError()
				if not validate_point(base):
					raise ValueError()
				if type(radius) not in (int, float) or radius <= 0:
					raise ValueError()
				if type(height) not in (int, float) or height <= 0:
					raise ValueError()
			elif style == 'union':
				[validate_info(x) for x in data[1:]]
			else:
				raise ValueError()

		try:
			validate_info(data)
		except ValueError:
			tell(user, "Invalid JSON, see /help json for schema.")
			return

		zone = new_zone(name, data, user.username)

	else:
		args = filter(None, args.split())
		style = args.pop(0)
		try:
			dim = int(args.pop(0))
			if dim not in (-1,0,1):
				raise ValueError()
			args = [float(arg) for arg in args]
			if style == 'cube':
				if len(args) != 6:
					raise ValueError()
				point1 = args[:3]
				point2 = args[3:]
				zone = new_zone(name, ('cube',dim,point1,point2), user.username)
			elif style == 'cylinder':
				if len(args) != 5:
					raise ValueError()
				base = args[:3]
				radius, height = args[3:]
				if radius <= 0 or height <= 0:
					raise ValueError()
				zone = new_zone(name, ('cylinder',dim,base,radius,height), user.username)
			else:
				raise ValueError			
		except ValueError:
			tell(user, "Bad args.")
			return

	if zone is None:
		tell(user, "Unknown error while creating zone")
	else:
		tell(user, "Success. Remember that you still need an op to confirm the zone.")


def zonedestroy(message, user, name):
	name = name.strip('"')

	try:
		zone = get_zones()[name]
	except KeyError:
		tell(user, "That zone doesn't exist!")
		return
	if not controls_zone(user.username, zone) and not user.username in ops():
		tell(user, "That isn't your zone.")
	get_zones().pop(name)
	tell(user, "Zone deleted.")


def helplist(message, user):
	tell(user, "The /zone commands let you manage your zones.\n"
	           "In all commands below, <zone> should be replaced with\n"
	           "the name of a zone you control, eg. /zone view my_zone\n"
	           "If the name has a space in it, put it in double quotes.\n"
	           "/zone current - See a list of zones you control that you are currently in.\n"
	           "/zone view - See a list of zones you control.\n"
	           "/zone view <zone> - Get info on that zone.\n"
	           "/zone here - Get list of zones you are currently in, and your permissions.\n"
	           "/zone new - Create new zone using menu system.\n"
	           "/zone new <zone> <args> - Advanced only, see help page.\n"
	           "/zone destroy <zone> - Delete a zone permanently.\n"
	           "/zone help <command> - Get help on a command, eg. /zone help new\n")


def helpinfo(message, user, command):
	helptext = {
		'view': "If no zone given, shows a list of zone names.\n"
		        "If a zone name given (and you have ADMIN rights to it),"
		        "displays a bunch of information about the zone.\n"
		        "Not all this info is likely to be useful, but oh well.",
		'here': "List all zones that you are currently standing in.\n"
		        "Also gives what permissions you are allowed in that zone.\n",
		'destroy': "Delete a zone and all associated information.\n"
		           "This includes any plot protection the zone may have provided.\n"
		           "No, ops cannot undo this. Use only if you are really sure.",
		'new': "When used with nothing else given, ie. just /zone new, "
		       "opens menu that will make a new zone step by step.\n"
		       "For advanced use, give the zone name followed by bounds args.\n"
		       "Bounds definitions are one of the following:\n"
		       "__ cube <dim> <x1> <y1> <z1> <x2> <y2> <z2>\n"
		       "__ cylinder <dim> <x> <y> <z> <radius> <height>\n"
		       "__ json <json> (EXPERIMENTAL, MAY NOT WORK)\n"
		       "Note that <dim> should be 0,-1,1 for overworld, Nether, End\n"
		       "The json bounds defn is special. The remainder of the line "
		       "should be valid JSON. If you don't know what that is, ignore it. JSON schema "
		       "is given by typing /zone help json",
		'help': "Ha ha, you're really funny. If you're reading this\n"
		        "you know how to use the help function already, moron.",
		'json': "In these definitions, we use the syntax <name:type> or just <type>.\n"
		        "point := [<x:float>, <y:float>, <z:float>]\n"
		        "bounds_info :=\n"
		        "__ ['cube', <dim:int>, <point1:point>, <point2:point>] OR\n"
		        "__ ['cylinder', <dim:int>, <base:point>, <radius:float>,\n"
		        "____ <height:float>] OR\n"
		        "__ ['union', <bounds_info>, <bounds_info>, ...]\n"
		        "For example, the following describes a zone that covers both a cylinder "
		        "in Overworld and a cube in the Nether:\n"
		        "['union', ['cylinder', 0, [128,64,-128], 8, 64], \n"
		        "__ ['cube', -1, [64,64,-64], [80,128,-80]]]"
	}

	if command not in helptext:
		tell(user, "Unknown command: %s" % command)
	else:
		tell(user, helptext[command])
