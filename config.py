import os, sys, logging

#==============================================================================
#       MCProxy Debug Settings

# Debugging flag. Set by passing debug as an argument to proxy.py.
DEBUG = 'debug' in sys.argv

# Don't know what this is.
PASSTHROUGH = False

#==============================================================================
#       Network Settings

# Address to listen for player packets. Default is ('0.0.0.0', 25564)
LISTEN_ADDR = ('0.0.0.0', 25565) if not DEBUG else ('0.0.0.0', 25564)
# Address that the server is running on. Try something like ('127.0.0.1', 25564)
SERVER_ADDR = ('127.0.0.1', 25564)

#==============================================================================
#       Logging

#base log directory for all logs.
LOG_DIR = "/home/minecraft/server/MCProxy/logs/"

#path to logging file
LOG_FILE = os.path.join(LOG_DIR, 'proxy.log')
LOG_FORMAT = '%(created)f\t%(levelname)s\t%(message)s'
LOG_LEVEL = logging.INFO 

#passthrough log file
PASSTHROUGH_LOG_FILE = os.path.join(LOG_DIR, 'passthrough.log')

#==============================================================================
#       Plugins

PLUGIN_PATH = '/home/minecraft/server/MCProxy/plugins' if not DEBUG else './plugins'

#==============================================================================
#       Internal Server Options

# Directory containing the minecraft server.
SERVER_DIR = '/home/minecraft/server/bukkit'

# The screen alias that the server is running under.
# Example: screen -S minecraft_server_screen java -Xincgc -Xmx1024M -jar minecraft_server.jar 
SERVER_SCREEN_NAME = 'minecraft_server_screen'

# Server tick time. Minecraft uses 0.2 so this should not be changed.
TICK_INTERVAL = 0.2

# Place each world here. 
# In vanilla this is just te path to the 'world' directory. 
# In Bukkit this is the paths to the 'world', 'world_nether' and 
# 'world_the_end' directories.
WORLD_DIRS = [os.path.join(SERVER_DIR, 'world'), os.path.join(SERVER_DIR, 'world_nether'), os.path.join(SERVER_DIR, 'world_the_end')]

# Buff sizes - shouldn't change
MAX_SEND = 4096
MAX_RECV = 4096
