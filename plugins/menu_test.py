
"""A quick module to test the menu system"""

import player_cmd as cmd
import menus
from helpers import tell

def on_start():
	cmd.register('/menu-test', lambda msg, user: start_menu(user))


def on_packet(packet, user, to_server):
	return packet


def start_menu(user):
	try:
		menus.display(user, *ROOT_MENU)
	except menus.MenuLockError:
		tell(user, "Menu already open")

def exit_menu(user, value):
	tell(user, "Test menu closed")

def generate_menu(user, value):
	return (
		"You typed: %s\nSelect Continue to return to the top menu." % value,
		[("Continue", lambda u,v: ROOT_MENU)],
		lambda u,v: ROOT_MENU
	)

ROOT_MENU = (
	"Top testing menu. :exit to exit. See /menus for help.",
	[
		("Test a submenu", lambda u,v: SUB_MENU),
		("Test a prompt", lambda u,v: PROMPT_MENU),
		("Loop back to this menu", lambda u,v: ROOT_MENU)
	],
	exit_menu
)

SUB_MENU = (
	"Test sub-menu.\nPick the option below or :exit to return to top menu.",
	[("Return", lambda u,v: ROOT_MENU)],
	lambda u,v: ROOT_MENU
)

PROMPT_MENU = (
	"Respond with some text.",
	('prompt', generate_menu),
	lambda u,v: ROOT_MENU
)

