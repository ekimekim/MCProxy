import os, sys, logging

DEBUG = 'debug' in sys.argv
PASSTHROUGH = False

# Info for proxy
#LISTEN_ADDR = ('0.0.0.0', 25564)
LISTEN_ADDR = ('0.0.0.0', 25565) if not DEBUG else ('0.0.0.0', 25564)
#SERVER_ADDR = ('127.0.0.1', 25565)
SERVER_ADDR = ('127.0.0.1', 25042)
LOG_FILE = '/var/minecraft/logs/proxy.log' if not DEBUG else '/var/minecraft/logs/proxy-debug.log'
LOG_FORMAT = '%(created)f\t%(levelname)s\t%(message)s'
LOG_LEVEL = logging.INFO # if not DEBUG else logging.DEBUG
PASSTHROUGH_LOG_FILE = '/var/minecraft/logs/passthrough.log'
PLUGIN_PATH = '/var/minecraft/src/mcproxy/plugins' if not DEBUG else './plugins'
TICK_INTERVAL = 0.2

# Buff sizes - shouldn't change
MAX_SEND = 4096
MAX_RECV = 4096

# Info for plugins
SERVER_DIR = '/var/minecraft/survival'
WORLD_DIR = os.path.join(SERVER_DIR, 'world')
