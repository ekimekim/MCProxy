import sys
from config import *
sys.path.append(PLUGIN_PATH)

# Import plugins here
import log_all, log_sorted, usernames, no_changes, sp_opcolor, usercolors, bad_cmd
import player_cmd as cmd

# Set ordering here
plugins = []
plugins.append(log_sorted) # Always first to catch all raw packets
plugins.append(usernames) # The earlier the better, name the login packets sooner.
plugins.append(cmd) # Should probably be before anything that depends on it
plugins.append(usercolors)
plugins.append(bad_cmd) # Always last out of chat commands
