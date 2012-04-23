NAME = "slimeballs"
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = 'Gives the player two slimeballs every 24 hours.'

from helpers import server_cmd, tell, all_users
import player_cmd as cmd
import plugins

import os
import cPickle 
import time

INTERVAL = 24*60*60 # 24hrs

USER_TIMES = os.path.join(plugins.getPluginDir(NAME), "data")

times = {}


def on_start():
	cmd.register('/slimeballs', on_cmd)
	if os.path.isfile(USER_TIMES):
		for line in open(USER_TIMES,'ra'):
			pair = str(line).strip().split(' ')
			times[str(pair[0])] = int(pair[1])
	else:
		open(USER_TIMES,'w')
	f = open(USER_TIMES,'a')
	for n in all_users():
		if n not in times:
			t = int(time.time() - INTERVAL)
			times[n] = t
			f.write(n + " " + str(t) + "\n")
	
def on_packet(packet, user, to_server):
	if packet.name() == 'Login request' and to_server:
		uString = str(user)[:str(user).index("@")] 
		if uString not in times or INTERVAL - (time.time() - times[uString]) <= 0:
			tell(user, "Slimeballs: You have slime available. Run /slimeballs to collect.")
	return packet

def on_cmd(message, user):
	give = False
	now = int(time.time())
	uString = str(user)[:str(user).index("@")] 
	if uString in times:
		time_left = INTERVAL - (now - times[uString])
		if time_left <= 0:
			give = True
		else:
			hours = int(time_left / 3600)
			mins = int((time_left % 3600) / 60)
			secs = time_left - 3600*hours - 60*mins
			tell(user, "slimeballs: You cannot slimeballs again for another %2d:%2d:%2d" % (hours, mins, secs))
	else:
		give = True
		
	if give:
		
		tell(user, "slimeballs: Dispensing product.")
		server_cmd(unicode('/give ' + str(uString) + ' 341 2')) # give 2 slimeballs
		times[uString] = now
		f = open(USER_TIMES,'w')
		for user in times:
			f.write(unicode(user + " " + str(times[user]) + "\n"))

