
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """Newly created zones must be submitted for op approval.
Ops gain commands:
	/zone op help
	/zone op wool ZONE - Paint 10x10x10 area about and below op in green woll for requested zone, red wool other zone, yellow if both.
	/zone op confirm ZONE
	/zone op modify "ZONE" KEY VALUE
"""

import zones
from zones import get_zones
from player_cmd import register
from helpers import ops, send_packet
from plugin_helpers import tell, ops_only
from packet_decoder import Packet
from long_operations import long_operation

def set_confirm(zone):
	zone['confirmed'] = False

def on_start():
	zones.new_zone_hooks.append(set_confirm)
	register("/zone op help", ophelp)
	register("/zone op wool (.*)", zonewool)
	register("/zone op wool-all (.*)", zonewoolall)
	register("/wool", morewool)
	register("/zone op confirm (.*)", zoneconfirm)
	register('/zone op modify "([^"]+)" ([^ ]+) (.*)', zonemodify)


@ops_only
def ophelp(message, user):
	tell(user, "Note that unlike /zone commands, zone names are taken verbatim (no quotes).\n"
	           "/zone op help - Obvious.\n"
	           "/zone op wool <zone> - 10x10x10 cube below player highlighted as follows:\n"
	           "__ green: In given zone.\n"
	           "__ yellow: In zone besides one given.\n"
	           "__ red: In given zone AND at least one other.\n"
	           "__ You will need to log out/in to reverse changes.\n"
	           "/wool - Shortcut to re-run last wool command.\n"
	           "/zone op wool-all <zone> - Does wool for an entire zone.\n"
	           "/zone op confirm <zone> - Confirm zone.\n"
	           '/zone op modify "<zone>" <key> <value> - Advanced use. Quotes required.')


@ops_only
def zoneconfirm(message, user, name):
	if name not in zones.get_zones():
		tell(user, "Zone does not exist.")
		return
	zones.get_zones()[name]['confirmed'] = True
	tell(user, "Success")


WOOL_ID = 35 # Wool
IN_ZONE = 5 # green
OTHER_ZONE = 4 # yellow
CONFLICT = 14 # red

def wool_point(zone, user, (x,y,z)):
	block_metadata = None
	zones_here = zones.get_zones_at_point(user.dimension, (x,y,z))
	if zones_here == [zone]:
		block_metadata = IN_ZONE
	elif zone in zones_here:
		block_metadata = CONFLICT
	elif zones_here:
		block_metadata = OTHER_ZONE
	if block_metadata is not None:
		packet = Packet('Block change', x=x, y=y, z=z, id=WOOL_ID, metadata=block_metadata)
		send_packet(packet, user, False)


@ops_only
def zonewool(message, user, name):
	user.morewool = name
	try:
		zone = zones.get_zones()[name]
	except KeyError:
		tell(user, "Bad zone name")
		return
	base = [int(axis) for axis in user.position]
	for x in range(base[0]-5, base[0]+5):
		for y in range(base[1]-10, base[1]):
			for z in range(base[2]-5, base[2]+5):
				wool_point(zone, user, (x,y,z))
	tell(user, "Complete.")


@ops_only
@long_operation
def zonewoolall(message, user, name):
	yield
	EDGE = 4 # extra blocks beyond edges
	user.morewool = name
	try:
		zone = zones.get_zones()[name]
	except KeyError:
		tell(user, "Bad zone name")
		return
	if zone['bounds_info'][0] == 'cube':
		box = zone['bounds_info'][2:]
		box = zip(*box)
		box = [sorted(axis) for axis in box]
	elif zone['bounds_info'][0] == 'cylinder':
		(x, y, z), r, h = zone['bounds_info'][2:]
		box = ((x-r, x+r), (y, y+h), (z-r, z+r))
	else:
		tell(user, "Unsupported zone type: %s" % zone['bounds_info'][0])
		return
	box = [(int(a)-EDGE, int(b)+1+EDGE) for a,b in box]
	for y in range(*box[1]):
		for x in range(*box[0]):
			yield
			for z in range(*box[2]):
				wool_point(zone, user, (x,y,z))
		complete = float(y-box[1][0])/(box[1][1]-box[1][0])
		if complete < 1:
			tell(user, 'Wooling %s...%.2f%% complete' % (name, 100 * complete))
	tell(user, 'Complete.')


def morewool(message, user):
	if hasattr(user, 'morewool'):
		return zonewool(message, user, user.morewool)
	else:
		return False


@ops_only
def zonemodify(message, user, zone, key, value):
	if name not in zones.get_zones():
		tell(user, "Zone does not exist.")
		return
	zone = zones.get_zones()[zone]
	zone[key] = eval(value)
	tell(user, "Success")
