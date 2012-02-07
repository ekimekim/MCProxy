
#from gzip import GzipFile
#from StringIO import StringIO
import struct

from subprocess import Popen, PIPE
from fcntl import fcntl, F_SETFL, F_GETFL
from select import select
from os import O_NONBLOCK, write

def cmd(args, text):
	proc = Popen(args, stdin=PIPE, stdout=PIPE)
	output = ''
	set_non_blocking = lambda fd: fcntl(fd, F_SETFL, fcntl(fd, F_GETFL) | O_NONBLOCK)
	set_non_blocking(proc.stdin)
	set_non_blocking(proc.stdout)
	while proc.poll() is None:
		r,w,x = select([proc.stdout], [proc.stdin] if text else [], [], 0.1)
		if r:
			output += proc.stdout.read()
		if w:
			n = write(proc.stdin.fileno(), text)
			text = text[n:]
			if not text:
				proc.stdin.close()
	if proc.returncode:
		raise OSError(args, proc.returncode)
	r,w,x = select([proc.stdout], [], [], 0.1)
	if r:
		output += proc.stdout.read()
	return output

class BadNBTData(Exception):
	pass

def gen_unpack(fmt):
	"""Helper function. Generates a function that takes an arg, and unpacks it with the given format string."""
	def gen_fn(s):
		return struct.unpack(fmt, s)[0]
	return gen_fn

def gen_pack(fmt):
	"""Helper function. Generates a function that takes an arg, and packs it with the given format string."""
	def gen_fn(x):
		return struct.pack(fmt, x)
	return gen_fn

def read(f, n):
	if not n:
		return ''
	s = f.read(n)
	if len(s) != n:
		raise BadNBTData()
	return s

def gunzip(s):
	"""Unzips a string compressed with gzip compression (level 9)"""
	#return GzipFile(fileobj=StringIO(s), mode='r').read()
	return cmd(['gunzip'], s)

def gzip(s):
	"""Zips a string with gzip compression (level 9)"""
#	sio = StringIO()
#	gz = GzipFile(fileobj=sio, mode='w')
#	gz.write(s)
#	gz.close()
#	sio.seek(0)
#	return sio.read()
	return cmd(['gzip'], s)


class NBTCompound(dict):
	def __init__(self):
		self.order = []
	def __str__(self):
		return '{' + ', '.join(["%s: %s" % (key, self[key]) for key in self.order]) + '}'
	__repr__ = __str__


# For simple tags: dict of tag_id: (type, length, conversion_fn)
tags = {
	'\x00': ("end", 0, lambda s: None),
	'\x01': ("byte", 1, gen_unpack('!b')),
	'\x02': ("short", 2, gen_unpack('!h')),
	'\x03': ("int", 4, gen_unpack('!i')),
	'\x04': ("long", 8, gen_unpack('!q')),
	'\x05': ("float", 4, gen_unpack('!f')),
	'\x06': ("double", 8, gen_unpack('!d')),
}

def decode(data):
	"""Decodes a bytestring representation of nbt into an NBT object, as follows:
		All tag types become the following value:
			("type", value)
		Types and the kind of python value they become are as follows:
			"byte": integer
			"short": integer
			"int": integer
			"long": integer
			"float": float
			"double": float
			"byte array": (integer, ...)
			"string": str
			"list": ("inner type", [as per inner type])
			"compound": {tag name: tag value as per this documentation}
		So, in general, a NBT object is a dict containing tuples of (type, value).
		At the highest level, returns the value of the outermost compound.
		NOTE: compound is not actually a dict, but can be treated like one.
		However, if you want minecraft to understand what you send you probably shouldn't
		add or remove any fields (or even remove/readd).
		If you wish to create your own, instantiate the NBTCompound class, then treat it like a dict.
		However, set the order member to be a list of keys, which is the order the values will be written in.
	"""
	original = data[:]
	f = StringIO(data)
	try:
		name, value = _decode(f)
		if value is None:
			raise BadNBTData()
		compound, value = value
		if compound != "compound":
			raise BadNBTData()
	except BadNBTData, ex:
		ex.args = (original,)
		raise
	return value

def _decode(f):
	"""Returns (Name, (Type, Value)), or ('', None) for end"""
	tag = read(f, 1)
	if tag == '\x00':
		return '', None
	name = get_str(f)
	return name, get_val(tag, f)

def get_val(tag, f):
	"""Returns (Type, Value), or None for end"""
	if tag in tags:
		typename, length, fn = tags[tag]
		return typename, fn(read(f,length))
	if tag == '\x07':
		length = struct.unpack('!i', read(f,4))[0]
		if length < 0:
			raise BadNBTData()
		data = struct.unpack('!'+'b'*length, read(f,length))
		return "byte array", data
	if tag == '\x08':
		return "string", get_str(f)
	if tag == '\x09':
		inner = read(f,1)
		if inner == 0:
			raise BadNBTData()
		length = struct.unpack('!i', read(f, 4))[0]
		if length < 0:
			raise BadNBTData()
		data = [get_val(inner, f) for x in range(length)]
		datatype = data[0][0]
		data = [x[1] for x in data]
		return "list", (datatype, data)
	if tag == '\x0a':
		d = NBTCompound()
		while 1:
			name, value = _decode(f)
			if value is None:
				return "compound", d
			d[name] = value
			d.order.append(name)

def get_str(f):
	"""Return a string read from the input stream"""
	length = struct.unpack('!H', read(f, 2))[0]
	return read(f, length)


# For simple tags: dict of tag_id: (type, length, conversion_fn)
reverse_tags = {
	'end': ("\x00", lambda s: None),
	'byte': ("\x01", gen_pack('!b')),
	'short': ("\x02", gen_pack('!h')),
	'int': ("\x03", gen_pack('!i')),
	'long': ("\x04", gen_pack('!q')),
	'float': ("\x05", gen_pack('!f')),
	'double': ("\x06", gen_pack('!d')),
}

all_tag_ids = {
	'end': '\x00',
	'byte': '\x01',
	'short': '\x02',
	'int': '\x03',
	'long': '\x04',
	'float': '\x05',
	'double': '\x06',
	'byte array': '\x07',
	'string': '\x08',
	'list': '\x09',
	'compound': '\x0a'
}

def encode(nbt):
	"""The reverse operation to decode. Takes an nbt object as output by decode and returns the bytestring representation."""
	# TODO error handling
	assert type(nbt) == NBTCompound, "NBT object a %s, not a NBTCompound" % type(nbt)
	f = StringIO()
	_encode(f, '', "compound", nbt)
	return f.getvalue()

def to_str(s):
	"""Turn string into packed form"""
	return struct.pack('!H', len(s)) + s

def _encode(f, name, nbttype, value):
	f.write(all_tag_ids[nbttype])
	f.write(to_str(name))
	encode_value(f, nbttype, value)

def encode_value(f, nbttype, value):
	if nbttype in reverse_tags:
		tag_id, fn = reverse_tags[nbttype]
		f.write(fn(value))
	elif nbttype == 'byte array':
		length = len(value)
		f.write(struct.pack('!i',length))
		f.write(struct.pack('!'+'b'*length, *value))
	elif nbttype == 'string':
		f.write(to_str(value))
	elif nbttype == 'list':
		inner, value = value
		f.write(all_tag_ids[inner])
		length = len(value)
		f.write(struct.pack('!i',length))
		for item in value:
			encode_value(f, inner, item)
	else:
		assert nbttype == 'compound', "NBT type is %s, not compound" % nbttype
		for name in value.order:
			innertype, innervalue = value[name]
			_encode(f, name, innertype, innervalue)
		f.write(all_tag_ids['end'])
