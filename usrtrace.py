"""On import, sets up SIGUSR1 to print a traceback as INFO for python logging"""

import signal, traceback
import logging

def log_traceback(sig, frame):
	tb = traceback.format_stack()
	tb = ''.join(tb)
	logging.info("Recieved SIGUSR1, printing traceback:\n" + tb)

signal.signal(signal.SIGUSR1, log_traceback)
