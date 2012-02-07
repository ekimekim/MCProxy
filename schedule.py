import time
from signal import SIGALRM

events = [] # (time, event) - time is float epoch
done_events = [] # (time, event) - events that passed while alarm_lock was True
alarm_lock = False

def schedule(delay, callback_fn):
	"""Schedule callback_fn to run after delay seconds."""
	raise NotImplemetedError()
#	global alarm_lock, events, done_events
#
#	if delay <= 0:
#		raise ValueError("Delay must be positive")
#
#	now = time.time()
#	new_time = now + delay
#
#	alarm_lock = True # During this time, alarm handler will log anything it does to done_events
#	for i in range(len(events)):
#		if new_time < events[i][0]:
#			events.insert(i, (new_time, callback_fn))
#			break
#	else: # Time is after all current events
#		events.append((new_time, callback_fn))
#	alarm_lock = False # No longer adding to done_events
#
#	# Check done_events for anything that happened in critical section
#	for event in done_events:
#		try:
#			events.remove(event)
#		except ValueError:
#			pass
