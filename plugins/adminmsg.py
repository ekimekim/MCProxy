NAME = "adminmsg"
AUTHOR = 'ekimekim'
CONTACT = 'mikelang3000@gmail.com'
DESCRIPTION = """A simple plugin that saves offline messages for admins to read. Ops and the server are allerted when they log in."""

import player_cmd as cmd
import time
import plugins
from os import path
import os
from plugin_helpers import tell
from helpers import  ops, color, colors, server_cmd

ADMIN_MSG_FILE = path.join(plugins.getPluginDir(NAME)  ,'admin.msg')
adminfile = None


def on_start():
    cmd.register(r'/admin (.*)', on_cmd)  
    if path.isfile(ADMIN_MSG_FILE):
        f = open(ADMIN_MSG_FILE, 'r')
        if f.read(1) is not None:
            server_cmd("/say " + color("red") + "There are admin messages pending.")

def on_packet(packet, user, to_server):
    if packet.name() == 'Login request' and to_server:
        uString = str(user)[:str(user).index("@")] 
        if uString in ops() and path.isfile(ADMIN_MSG_FILE):
            f = open(ADMIN_MSG_FILE, 'r')
            if f.read(1) is not None:
                tell(user, color("red") + "There are admin messages pending.")
    return packet

def on_cmd(message, user, args):
    if path.isfile(ADMIN_MSG_FILE):
        adminfile = open(ADMIN_MSG_FILE, 'a')
    else:
        adminfile = open(ADMIN_MSG_FILE, 'w')
    adminfile.write("[%s] %s sent: %s\n" % (time.time(), user, message[len("/admin "):]))
    tell(user, 'Message sent.')
