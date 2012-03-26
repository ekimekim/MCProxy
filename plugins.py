import sys
from config import *
sys.path.append(PLUGIN_PATH)

# Import plugins here
import log_all, log_sorted, usernames, no_changes, sp_opcolor, usercolors, bad_cmd, welcome, menus, timed_events
import player_cmd as cmd
import menu_test

# Set ordering here
plugins = []
plugins.append(log_all)
plugins.append(log_sorted) # Always first to catch all raw packets
plugins.append(usernames) # The earlier the better, name the login packets sooner.
plugins.append(schedule) # Before anything that depends on it.
plugins.append(plugin_helpers) # Lots of things depend on this. Do it early.
plugins.append(timed_events) # Before anything that depends on it. Not working yet.
plugins.append(cmd) # Should probably be before anything that depends on it
plugins.append(welcome) # Has /help, so high priority. But should be after usernames (for the welcome)
plugins.append(menus) # Should probably be before anything that depends on it
plugins.append(usercolors)
plugins.append(menu_test)
plugins.append(bad_cmd) # Always last out of chat commands
