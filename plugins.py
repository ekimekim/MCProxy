

import sys
import os
from config import *
sys.path.append(PLUGIN_PATH)

plugins = []
imports = {}
paths = {}


def addPlugin(pluginName, hasDir = False):
    """ Import a plugin. If the hasDir flag is raised a directory for the plugin in the plugin path is created if it doesn't already exist. """
    if hasDir:
        path = os.path.join(PLUGIN_PATH, pluginName)
        if not os.path.exists(path):
            os.makedirs(path)
        paths[pluginName] = path
    else:
       paths[pluginName] = None 
    plugin = __import__(pluginName)
    imports[pluginName] = plugin
    plugins.append(plugin)
    

def addAliasPlugin(pluginName,alias, hasDir = False):
    """ Import a plugin and refer to it as the alias. If the hasDir flag is raised a directory for the plugin is created in the plugin path if it doesn't already exist under both the plugin name and the alias. """
    if hasDir:
        path = os.path.join(PLUGIN_PATH, pluginName)
        if not os.path.exists(path):
            os.makedirs(path)
        paths[alias] = path
        paths[pluginName] = path
    else:
        paths[alias] = None
        paths[pluginName] = None 
    plugin = __import__(pluginName)
    plugin.__name__ = alias
    imports[alias] = plugin
    plugins.append(plugin)
        
def getPluginDir(pluginName):
    """Returns the path to the plugin directory of the plugin if the plugin has one or None otherwise."""
    return paths[pluginName]
    
def getPlugin(pluginName):
    return imports[pluginName]
    
# basic logging
#addPlugin("log_all")               # Only on when needed - chews disk space
addPlugin("log_sorted")             # Always first to catch all raw packets

# utility
addPlugin("usernames")              # The earlier the better, name the login packets sooner.
addPlugin("schedule")               # Should probably be before anything that depends on it
addPlugin("persistent_store",True)  # MUST be before anything that uses it
addPlugin("plugin_helpers")         # Lots of things depend on this. Do it early.

addAliasPlugin("player_cmd", "cmd") # Should probably be before anything that depends on it       
addPlugin("menus")                  # Should probably be before anything that depends on it  

# features
addPlugin("welcome")                # Has /help, so high priority. But should be after usernames (for the welcome)
addPlugin("adminmsg", True)
addPlugin("usercolors")
addPlugin("slimeballs",True) 

#addPlugin("no_changes") 






