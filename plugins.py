import sys
from config import *
sys.path.append(PLUGIN_PATH)

# Import plugins here
import log_all, log_sorted, usernames, no_changes, sp_opcolor, usercolors, bad_cmd, welcome, menus, schedule, plugin_helpers, zones, persistent_store
import acls, dotstrip
import player_cmd as cmd
import menu_test, testing
import zone_create_menu, zone_cmds, acl_cmds, zone_confirm, long_operations, ban_ips

# Set ordering here

plugins = []

# basic logging
#plugins.append(log_all) # Only on when needed - chews disk space
plugins.append(log_sorted) # Always first to catch all raw packets

# utility
plugins.append(usernames) # The earlier the better, name the login packets sooner.
plugins.append(schedule) # Should probably be before anything that depends on it
plugins.append(persistent_store) # MUST be before anything that uses it in on_start
plugins.append(long_operations)
plugins.append(plugin_helpers) # Lots of things depend on this. Do it early.
plugins.append(zones) # The earlier, the more up to date positions are
plugins.append(cmd) # Should probably be before anything that depends on it
plugins.append(menus) # Should probably be before anything that depends on it

# features
plugins.append(ban_ips)
plugins.append(welcome) # Has /help, so high priority. But should be after usernames (for the welcome)
plugins.append(acls)
plugins.append(dotstrip) # Must be before usercolors
plugins.append(usercolors)
plugins.append(zone_create_menu)
plugins.append(zone_cmds)
plugins.append(zone_confirm)
plugins.append(acl_cmds)

#plugins.append(testing)

# tail
plugins.append(bad_cmd) # Always last out of chat commands
