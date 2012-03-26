import time

events = [] # (time, event) - time is float epoch

def schedule(delay, callback_fn):
	"""Schedule callback_fn to run after (at least) delay seconds."""
	new_time = time.time() + delay
	for i in range(len(events)):
		event_time, event = events[i]
		if event_time > new_time:
			events.insert(i, (new_time, callback_fn))
			break
	else:
		events.append((new_time, callback_fn))

def on_tick(users):
	now = time.time()
	while events and now >= events[0][0]:
		events[0][1]()
		events.pop(0)
