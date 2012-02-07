
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = 'Gives the player two slimeballs every 24 hours.'

from helpers import server_cmd, tell
import player_cmd as cmd
import time

users = {}
INTERVAL = 24*60*60 # 24hrs

def on_start():
	cmd.register('/slimeballs', on_cmd)

def on_packet(packet, user, to_server):
	return packet

def on_cmd(message, user):
	now = time.time()
	user_time = users.get(user.username, 0)
	time_left = INTERVAL - (now - user_time)
	if time_left <= 0:
		tell(user, "slimeballs: Dispensing product.")
		server_cmd('/give %s 341 2') # give 2 slimeballs
		users[user.username] = now
	else:
		hours = int(time_left % 3600)
		mins = int(time_left % 60 - 60*hours)
		secs = int(time_left - 3600*hours - 60*mins)
		tell(user, "slimeballs: You cannot slimeballs again for another %02d:%02d:%02d" % (hours, mins, secs))

