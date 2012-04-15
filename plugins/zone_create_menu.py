
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """A menu for defining new zones then submitting them for op approval."""

from menus import display, MenuLockError


def start_menu(message, user):
	try:
		display(ROOT_MENU)
	except MenuLockError:
		tell(user, "You already have a menu open.\nTry :again to see it or :exit to quit it.")


def exit_menu(user, value):
	tell(user, "Zone creation cancelled")


def from_name(user, name):
	if name in get_zones():
		tell(user, "That name is already in use.")
		return ROOT_MENU

	return (
		"The new zone will be called %s.\n"
		"Please pick a basic shape for the new zone.\n",
		[
			("Cube", lambda u,v: from_cube(u, v, name)),
			("Cylinder", lambda u,v: from_cyl(u, v, name))
		],
		exit_menu
	)


def from_cube(user, value, name):
	return (
		"You will need to give two points to create the cube.\n"
		"To set the first point, either type the coords as :X,Y,Z\n"
		"or just type ':' to use your current position (at your feet)",
		('prompt', lambda u,v: from_cube_pt1(u, v, name)),
		exit_menu
	)


def get_point(user, value):
	if not value:
		return user.position
	try:
		point = [float(x.strip()) for x in value.split(',')]
	except ValueError:
		point = []
	if len(point) != 3:
		tell(user, "Badly formatted response. For example,\n"
		           "the point at x=100, y=64, z=-100 would be typed as\n"
		           ":100,64,-100")
		raise ValueError
	return point


def from_cube_pt1(user, value, name):
	try:
		point1 = get_point(user, value)
	except ValueError:
		return from_cube(user, None, name)
	return (
		"Set first point at (%.2f,%.2f,%.2f)\n"
		"Please set the second point in the same way." % point1,
		('prompt', lambda u,v: from_cube_pt2(u, v, name, point1)
	)


def from_cube_pt2(user, value, name, point1):
	try:
		point2 = get_point(user, value)
	except ValueError:
		return from_cube_pt1(user, ",".join([str(x) for x in point1]), name)
	tell(user, "Set second point at (%.2f,%.2f,%.2f)" % point2)
	return make_zone(user, name, ('cube', user.dimension, point1, point2))


def make_zone(user, name, bounds_info):
	if new_zone(name, bounds_info, user.username, confirmed=False) is None:
		tell(user, "An error occurred while creating the zone. Try again or call an op.")
	else:
		# TODO something about op confirming it later
		tell(user, "Zone %s created. Exiting menu." % name)


def from_cyl(user, value, name):
	return (
		"First, tell me the centre point of the base of the cylinder.\n"
		"To set the point, either type the coords as :X,Y,Z\n"
		"or just type ':' to use your current position (at your feet)",
		('prompt', lambda u,v: from_cyl_pt(u, v, name)),
		exit_menu
	)


def from_cyl_pt(user, value, name):
	try:
		point = get_point(user, value)
	except ValueError:
		return from_cyl(user, None, name)
	return (
		"Set base point at (%.2f,%.2f,%.2f)\n"
		"Please give the cylinder radius (how far out it extends)." % point,
		# TODO UPTO
		('prompt', lambda u,v: from_cyl_radius
	)


ROOT_MENU = (
	"This is the zone creation menu.\n"
	"Type :exit to quit at any time.\n"
	"First, please give this zone a name.\n",
	('prompt', from_name),
	exit_menu
)
