import sys
from config import *
sys.path.append(PLUGIN_PATH)

# Import plugins here
import log_all, log_sorted, usernames, no_changes, sp_opcolor

# Set ordering here
plugins = [log_sorted, usernames, sp_opcolor]
