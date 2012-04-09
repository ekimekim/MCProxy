import sys
from config import *
sys.path.append(PLUGIN_PATH)

# Import plugins here
import log_all, log_sorted, usernames, no_changes, sp_opcolor, usercolors, bad_cmd, welcome, menus, schedule, plugin_helpers, zones, persistent_store
import player_cmd as cmd
import menu_test, testing

# Set ordering here

plugins = []

# basic logging
#plugins.append(log_all) # Only on when needed - chews disk space
plugins.append(log_sorted) # Always first to catch all raw packets

# utility
plugins.append(usernames) # The earlier the better, name the login packets sooner.
plugins.append(schedule) # Should probably be before anything that depends on it
plugins.append(persistent_store) # MUST be before anything that uses it
plugins.append(plugin_helpers) # Lots of things depend on this. Do it early.
plugins.append(zones) # The earlier, the more up to date positions are
plugins.append(cmd) # Should probably be before anything that depends on it
plugins.append(menus) # Should probably be before anything that depends on it

# features
plugins.append(welcome) # Has /help, so high priority. But should be after usernames (for the welcome)
plugins.append(usercolors)
plugins.append(menu_test)

plugins.append(testing)

# tail
plugins.append(bad_cmd) # Always last out of chat commands
