"""Helper functions for plugins"""

import os


from proxy import send_packet
from proxy import server_cmd as cmd
from config import *

def ops():
	"""Get list of op usernames."""
	open(os.path.join(SERVER_DIR, 'ops.txt'))
