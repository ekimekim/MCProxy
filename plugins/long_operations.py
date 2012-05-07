
AUTHOR = "ekimekim"
CONTACT = "mikelang3000@gmail.com"
DESCRIPTION = """This plugin allows for a function that takes a long time
to do so in a way that will not cause a massive server lag.
It does so with cooperative yields back to the main proxy.

Usage:
@long_operation
def my_big_func():
	yield
	i = 0
	for x in many_things:
		do_something(x)
		i += 1
		if i >= 1000:
			i = 0
			yield

This function will do_something with x 1000 times before allowing the proxy to continue.
It will do so every tick until complete.

The return value (as it appears to the outside function) is the first value yielded.
It is good practice to (as above) yield the return value early on, even if not distinct from later yields.
This is especially important as the function must always yield at least once.
Later yield values are ignored.
"""


def on_start():
	global running
	running = []


def on_tick(users):
	global running
	for fn in running[:]:
		try:
			next(fn)
		except (Exception, StopIteration):
			running.remove(fn)


def long_operation(fn):
	def _long_operation(*args, **kwargs):
		global running
		gen = fn(*args, **kwargs)
		running.append(gen)
		return next(gen)
	return _long_operation
