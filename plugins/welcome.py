
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """This module covers basics like a welcome message on login,
as well as your general /help, /firsttime, /rules stuff."""


import player_cmd as cmd
from helpers import tell


WELCOME = """Welcome to the BlockSoc server.
New here? Type /firsttime to get started.

Currently using MCProxy on our server.
Report any problems or suggestions to the 
Facebook group.

(TEMP) If you cannot connect, try accessing the
server via 'gamer.gg:25564'. This will (for now)
bypass MCProxy.
"""


HELP = """Commands and further help:
/firsttime:       First time here? READ THIS.
/rules:           Ignorance is no excuse. READ!!!
/help:            This.
/HELP:            Craftbukkit help.
/info:            Further info on the server.
/tech:            Technical details of MCProxy.
/color help:      Get help on the chat color system.
/admin [message]: Send an offline message to ops.
/slimeballs:      Get 2 slimeballs once a day.
"""

FIRSTTIME = """This is the Minecraft server for the UNSW Arc
group: BlockSoc.

Need to talk? Contact us via the BlockSoc 
Facebook group. Hate Facebook? So do I. 

The server is currently a CraftBukkit build run 
behind MCProxy. See /info for a list current 
active mods and /tech for information on MCProxy.

/help will give you MCProxy command help, 
/HELP will give you CraftBukkit command help.

Finally, read the rules (/rules) and have fun.
"""

RULES = """Most of this is obvious, really.
1. All ops decisions supercede these rules.
2. Do not be an asshole. Do not steal,
   grief or damage property.
3. Do not cheat. Do not dupe items,
   use fly hacks or xray mods.
"""

INFO = """This is the Minecraft server for the 
UNSW Arc group BlockSoc.

This server is currently using a modified
version of MCProxy by ekimekim (google it for git).

Active Bukkit Mods (/HELP):
 CreeperMess:   Message when a creeper explodes.
 SilkSpawners: Silk touch works on spawners.
 Lockette:     Lockable chests.
 MobRider:     Can use saddles on more mobs.
 PickBoat:     Boats break into boats.

Active MCProxy Plugins (/help, /tech):
 Adminmsg:     Send offline messages to admin.
 Usercolor:    Color scheme for usernames.
 Slimeballs:   Gives users 2 slimballs a day.
"""

TECH = """Most modified minecraft servers use bukkit,
or an equivilent modding framework. However, directly
modding the minecraft_server.jar makes new versions
a pain to support. We aim to be always cutting edge
and support features others can't, by using our
new technology: The MC Proxy.
The proxy sits between you and the server, watching
packets that go between. It can also modify, drop or
even generate packets, allowing for powerful control
over what the client and the server sees.
...you think the Server sent this message?
"""


def on_start():
	cmd.register('/news', lambda msg, user: tell(user, WELCOME))
	cmd.register('/help', lambda msg, user: tell(user, HELP))
	cmd.register('/firsttime', lambda msg, user: tell(user, FIRSTTIME))
	cmd.register('/rules', lambda msg, user: tell(user, RULES))
	cmd.register('/info', lambda msg, user: tell(user, INFO))
	cmd.register('/tech', lambda msg, user: tell(user, TECH))


def on_packet(packet, user, to_server):
	if packet.name() == 'Login request' and to_server:
		tell(user, WELCOME)
	return packet
