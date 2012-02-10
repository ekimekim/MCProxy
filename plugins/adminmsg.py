
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """A simple plugin that saves offline messages for admins to read
when they next log into the server shell"""

import player_cmd as cmd
import time

adminfile = None
ADMIN_MSG_FILE = '/var/minecraft/admin.msg'

def on_start():
	adminfile = open(ADMIN_MSG_FILE, 'a')
	cmd(r'/admin (.*)', on_cmd)

def on_packet(packet, user, to_server):
	return packet

def on_cmd(message, user, text):
	adminfile.write("[%s] %s sent: %s\n" % (time.time(), user, text))
	tell(user, 'Message sent.')
