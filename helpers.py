"""Helper functions for plugins"""

import os


from proxy import send_packet
from proxy import server_cmd as cmd
from config import *

def ops():
	"""Get list of op usernames."""
	ret = open(os.path.join(SERVER_DIR, 'ops.txt')).read().strip().split('\n')
	ret = [unicode(name) for name in ret]
	return ret
