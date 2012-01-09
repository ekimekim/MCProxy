from traceback import format_exc

emit = None

def init(emit_fn):
	global emit
	emit = emit_fn

def log_fn(fn):
	level = fn.__name__
	def generated_fn(msg, *args, **kwargs):
		exc_info = kwargs.get('exc_info', 0)
		if not emit:
			raise Exception("Logging not initialised")
		if args:
			msg %= args
		if exc_info:
			msg += '\n' + format_exc()
		emit(level, msg)
	generated_fn.__name__ = level
	return generated_fn

@log_fn
def debug():
	pass

@log_fn
def info():
	pass

@log_fn
def warning():
	pass

@log_fn
def error():
	pass

def exception(msg, *args):
	error(msg, *args, exc_info=1)

@log_fn
def critical():
	pass
