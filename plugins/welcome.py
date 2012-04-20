
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """This module covers basics like a welcome message on login,
as well as your general /help, /firsttime, /rules stuff."""


import player_cmd as cmd
from helpers import tell


WELCOME = "Hey guys! The map has been frozen and will reset back to the snapshot " \
	"every hour. You all have creative mode enabled, so go nuts! " \
	"And make sure to be online at 4pm Saturday, when the new map comes in!\n" \
	"The snapshot is available online at http://49.156.19.217/snapshot.tar.gz"


HELP = """Commands and further help:
/firsttime: First time here? READ THIS.
/rules: Ignorance is no excuse. READ!!!
/info: Plans for the future.
/news: Re-send the login message.
TODO /admin: Send a message. Admins will read it later.
/color help: Get help on the chat color system.
/zone help: Get help on the zone system
/acls help: Get help on getting plot protection
The following standard minecraft commands also work:
/tell PLAYER MESSAGE: Send a private MESSAGE to PLAYER.
/kill: Suicide.
"""

FIRSTTIME = """Welcome to ekimekim's server!
First and foremost, read /rules.
This is a survival server. You can build, but
you have to get the resources first!
While we employ anti-griefing technology,
mostly in the form of plot protection,
we are otherwise a vanilla gameplay server.
Problems? Contact me via my email:
mikelang3000@gmail.com
"""

RULES = """Most of this is obvious, really.
1. All ops decisions supercede these rules.
2. Do not be an asshole. Do not steal,
   grief or damage property.
3. Do not cheat. Do not dupe items,
   use fly hacks or xray mods.
4. Feel free to claim any unclaimed areas.
   Mark them out with a zone. You'll need
   to get them approved by an op for the
   plot protection to work, though.
5. Respects to OrionVM for free,
   high-performance hosting for this server!
"""

INFO = """This server is currently undergoing changes.
Long term, we hope to have the following layout:
A survival server - Plot protected but not much else.
This will carry over from the current map.
A creative server - Plot protected and with some
optional extra content.
A Role Playing server - This will be heavily modified.
Talk to bitblitz about ideas for this new map!
If you want more info on the technology we use, type '/tech'
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
