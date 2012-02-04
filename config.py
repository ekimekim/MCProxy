import os

# Info for proxy
LISTEN_ADDR = ('0.0.0.0', 25565)
SERVER_ADDR = ('127.0.0.1', 25042)
LOG_FILE = '/var/minecraft/logs/proxy.log'
PLUGIN_PATH = '/var/minecraft/Proxy2/plugins'

# Buff sizes - shouldn't change
MAX_SEND = 4096
MAX_RECV = 4096

# Info for plugins
SERVER_DIR = '/var/minecraft/'
WORLD_DIR = os.path.join(SERVER_DIR, 'world')
