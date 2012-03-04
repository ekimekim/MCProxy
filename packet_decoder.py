#!/usr/bin/python

import struct
import sys

#TODO: Review which of these we actually need
NODE_SERVER = 0x01
SERVER_TO_CLIENT = 0x01
FROM_SERVER = 0x01
TO_CLIENT = 0x01

NODE_CLIENT = 0x02
CLIENT_TO_SERVER = 0x02
FROM_CLIENT = 0x02
TO_SERVER = 0x02

EVENT_CLIENT_CONNECT = 0x00
EVENT_CLIENT_DISCONNECT = 0x01
EVENT_SERVER_DISCONNECT = 0x02

PROTOCOL_VERSION = 23

class Packet:
	def __init__(self):
		self.direction = 0
		self.ident = 0
		self.data = {}
		self.process = True
		self.transmit = True

	def name(self):
		return names[self.ident]

	def __str__(self):
		from_to = {CLIENT_TO_SERVER: "to server", SERVER_TO_CLIENT: "from server"}[self.direction]
		return "%s packet %s: %s" % (self.name(), from_to, repr(self.data))

	def copy(self):
		p = Packet()
		p.direction = self.direction
		p.ident = self.ident
		p.process = self.process
		p.transmit = self.transmit
		p.data = self.data.copy()
		return p


SLOT_EXTRA_DATA_IDS = [
	0x103, 0x105, 0x15A, 0x167,
	0x10C, 0x10D, 0x10E, 0x10F, 0x122,
	0x110, 0x111, 0x112, 0x113, 0x123,
	0x10B, 0x100, 0x101, 0x102, 0x124,
	0x114, 0x115, 0x116, 0x117, 0x125,
	0x11B, 0x11C, 0x11D, 0x11E, 0x126,
	0x12A, 0x12B, 0x12C, 0x12D,
	0x12E, 0x12F, 0x130, 0x131,
	0x132, 0x133, 0x134, 0x135,
	0x136, 0x137, 0x138, 0x139,
	0x13A, 0x13B, 0x13C, 0x13D ]

data_types = {
	"ubyte":  ('B', 1),
	"byte":   ('b', 1),
	"bool":   ('?', 1),
	"short":  ('h', 2),
	"float":  ('f', 4),
	"int":    ('i', 4),
	"double": ('d', 8),
	"long":   ('q', 8)
}

names = {
	0x00:	"Keep-alive",
	0x01:	"Login request",
	0x02:	"Handshake",
	0x03:	"Chat message",
	0x04:	"Time update",
	0x05:	"Entity Equipment",
	0x06:	"Spawn position",
	0x07:	"Use entity",
	0x08:	"Update health",
	0x09:	"Respawn",
	0x0A:	"Player",
	0x0B:	"Player position",
	0x0C:	"Player look",
	0x0D:	"Player position & look",
	0x0E:	"Player digging",
	0x0F:	"Player block placement",
	0x10:	"Holding change",
	0x11:	"Use bed",
	0x12:	"Animation",
	0x13:	"Entity action",
	0x14:	"Named entity spawn",
	0x15:	"Pickup spawn",
	0x16:	"Collect item",
	0x17:	"Add object or vehicle",
	0x18:	"Mob spawn",
	0x19:	"Entity: painting",
	0x1A:	"Experience Orb",
	0x1B:	"Stance update (DEPRECATED)",
	0x1C:	"Entity velocity",
	0x1D:	"Destroy entity",
	0x1E:	"Entity",
	0x1F:	"Entity relative move",
	0x20:	"Entity look",
	0x21:	"Entity look and relative move",
	0x22:	"Entity teleport",
	0x23:	"Entity head look",
	0x26:	"Entity status",
	0x27:	"Attach entity",
	0x28:	"Entity metadata",
	0x29:	"Entity effect",
	0x2A:	"Remove entity effect",
	0x2B:	"Experience",
	0x32:	"Pre-chunk",
	0x33:	"Map chunk",
	0x34:	"Multi-block change",
	0x35:	"Block change",
	0x36:	"Block action",
	0x3C:	"Explosion",
	0x3D:	"Sound effect",
	0x46:	"New or invalid state",
	0x47:	"Thunderbolt",
	0x64:	"Open window",
	0x65:	"Close window",
	0x66:	"Window click",
	0x67:	"Set slot",
	0x68:	"Window items",
	0x69:	"Update progress bar",
	0x6A:	"Transaction",
	0x6B:	"Creative inventory action",
	0x6C:	"Enchant Item",
	0x82:	"Update sign",
	0x83:	"Map data",
	0x84:	"Update tile entity",
	0xC8:	"Increment statistic",
	0xC9:	"Player List Item",
	0xFA:	"Plugin message",
	0xFE:	"Server list ping",
	0xFF:	"Disconnect"
}

structs = {
	#Keep-alive
	0x00: ("int", "keep_alive_id"),
	#Login request
	0x01:	{
		CLIENT_TO_SERVER: (
			("int", "protocol_version"),
			("string16", "username"),
			("string16", "level type"),
			("int", "server_mode"),
			("int", "dimension"),
			("byte", "difficulty"),
			("ubyte", "world_height"),
			("ubyte", "max_players")),
		SERVER_TO_CLIENT: (
			("int", "entity_id"),
			("string16", "unknown"),
			("string16", "level type"),
			("int", "server_mode"),
			("int", "dimension"),
			("byte", "difficulty"),
			("ubyte", "world_height"),
			("ubyte", "max_players"))},
	#Handshake
	0x02:	{
		CLIENT_TO_SERVER: ("string16", "username"),
		SERVER_TO_CLIENT: ("string16", "connection_hash")},
	#Chat message
	0x03: ("string16", "text"),
	#Time update
	0x04: ("long", "time"),
	#Entity Equipment
	0x05: (
		("int", "entity_id"),
		("short", "slot"),
		("short", "item_id"),
		("short", "damage")),
	#Spawn position
	0x06: (
		("int", "x"),
		("int", "y"),
		("int", "z")),
	#Use entity
	0x07: (
		("int", "subject_entity_id"),
		("int", "object_entity_id"),
		("bool", "left_click")),
	#Update health
	0x08: (
		("short", "health"),
		("short", "food"),
		("float", "food_saturation")),
	#Respawn
	0x09: (
		("int", "dimension"),
		("byte", "difficulty"),
		("byte", "server_mode"),
		("short", "world_height"),
		("long", "map_seed"),
		("string16", "level_type")),
	#Player
	0x0A: ("bool", "on_ground"),
	#Player position
	0x0B: (
		("double", "x"),
		("double", "y"),
		("double", "stance"),
		("double", "z"),
		("bool", "on_ground")),
	#Player look
	0x0C: (
		("float", "yaw"),
		("float", "pitch"),
		("bool", "on_ground")),
	#Player position & look
	0x0D:	{
		CLIENT_TO_SERVER: (
			("double", "x"),
			("double", "y"),
			("double", "stance"),
			("double", "z"),
			("float", "yaw"),
			("float", "pitch"),
			("bool", "on_ground")),
		SERVER_TO_CLIENT: (
			("double", "x"),
			("double", "stance"),
			("double", "y"),
			("double", "z"),
			("float", "yaw"),
			("float", "pitch"),
			("bool", "on_ground"))},
	#Player digging
	0x0E: (
		("byte", "status"),
		("int", "x"),
		("byte", "y"),
		("int", "z"),
		("byte", "face")),
	#Player block placement
	0x0F: (
		("int", "x"),
		("byte", "y"),
		("int", "z"),
		("byte", "direction"),
		("slot", "slot")),
	#Holding change
	0x10: ("short", "slot"),
	#Use bed
	0x11: (
		("int", "entity_id"),
		("byte", "in_bed"),
		("int", "x"),
		("byte", "y"),
		("int", "z")),
	#Animation
	0x12: (
		("int", "entity_id"),
		("byte", "animation")),
	#Entity action
	0x13: (
		("int", "entity_id"),
		("byte", "action")),
	#Named entity spawn
	0x14: (
		("int", "entity_id"),
		("string16", "player_name"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "rotation"),
		("byte", "pitch"),
		("short", "current_item")),
	#Pickup spawn
	0x15: (
		("int", "entity_id"),
		("short", "item"),
		("byte", "count"),
		("short", "metadata"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "rotation"),
		("byte", "pitch"),
		("byte", "roll")),
	#Collect item
	0x16: (
		("int", "subject_entity_id"),
		("int", "object_entity_id")),
	#Add object or vehicle
	0x17: (
		("int", "entity_id"),
		("byte", "type"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("int", "unknown")),
	#Mob spawn
	0x18: (
		("int", "entity_id"),
		("byte", "type"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "yaw"),
		("byte", "pitch"),
		("byte", "head yaw"),
		("metadata", "metadata")),
	#Entity: painting
	0x19: (
		("int", "entity_id"),
		("string16", "title"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("int", "direction")),
	#Experience Orb
	0x1A: (
		("int", "entity_id"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("short", "count")),
	#Stance update
	0x1B: (
		("float", "unknown1"),
		("float", "unknown2"),
		("float", "unknown3"),
		("float", "unknown4"),
		("bool", "unknown5"),
		("bool", "unknown6")),
	#Entity velocity
	0x1C: (
		("int", "entity_id"),
		("short", "x_velocity"),
		("short", "y_velocity"),
		("short", "z_velocity")),
	#Destroy entity
	0x1D: ("int", "entity_id"),
	#Entity
	0x1E: ("int", "entity_id"),
	#Entity relative move
	0x1F: (
		("int", "entity_id"),
		("byte", "x_change"),
		("byte", "y_change"),
		("byte", "z_change")),
	#Entity look
	0x20: (
		("int", "entity_id"),
		("byte", "yaw"),
		("byte", "pitch")),
	#Entity look and relative move
	0x21: (
		("int", "entity_id"),
		("byte", "x_change"),
		("byte", "y_change"),
		("byte", "z_change"),
		("byte", "yaw"),
		("byte", "pitch")),
	#Entity teleport
	0x22: (
		("int", "entity_id"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "yaw"),
		("byte", "pitch")),
	# Entity head look
	0x23: (
		("int", "entity_id"),
		("byte", "head yaw")),
	#Entity status
	0x26: (
		("int", "entity_id"),
		("byte", "status")),
	#Attach entity
	0x27: (
		("int", "subject_entity_id"),
		("int", "object_entity_id")),
	#Entity metadata
	0x28: (
		("int", "entity_id"),
		("metadata", "metadata")),
	# Entity effect
	0x29: (
		("int", "entity_id"),
		("byte", "effect_id"),
		("byte", "amplifier"),
		("short", "duration")),
	# remove entity effect
	0x2A: (
		("int", "entity_id"),
		("byte", "effect_id")),
	# Experience
	0x2B: (
		("float", "experience_bar"),
		("short", "level"),
		("short", "total_experience")),
	#Pre-chunk
	0x32: (
		("int", "x"),
		("int", "z"),
		("bool", "load")),
	#Map chunk
	0x33: (
		("int", "x"),
		("int", "z"),
		("bool", "contiguous"),
		("short", "bitmap"),
		("short", "add_bitmap"),
		("int", "data_size"),
		("int", "unknown")),
	#Multi-block change
	0x34: (
		("int", "x_chunk"),
		("int", "z_chunk"),
		("short", "record_count"),
		("int", "data_size")),
	#Block change
	0x35: (
		("int", "x"),
		("byte", "y"),
		("int", "z"),
		("byte", "id"),
		("byte", "metadata")),
	#Block action
	0x36: (
		("int", "x"),
		("short", "y"),
		("int", "z"),
		("byte", "type_state"),
		("byte", "pitch_direction")),
	#Explosion
	0x3C: (
		("double", "x"),
		("double", "y"),
		("double", "z"),
		("float", "unknown"),
		("int", "data_size")),
	#Sound effect
	0x3D: (
		("int", "effect_id"),
		("int", "x"),
		("byte", "y"),
		("int", "z"),
		("int", "extra")),
	#New or invalid state
	0x46: (
		("byte", "reason"),
		("byte", "gamemode")),
	#Thunderbolt
	0x47: (
		("int", "entity_id"),
		("bool", "unknown"),
		("int", "x"),
		("int", "y"),
		("int", "z")),
	#Open window
	0x64: (
		("byte", "window_id"),
		("byte", "inventory_type"),
		("string16", "window_title"),
		("byte", "slots_count")),
	#Close window
	0x65: ("byte", "window_id"),
	#Window click
	0x66: (
		("byte", "window_id"),
		("short", "slot"),
		("byte", "right_click"),
		("short", "transaction_id"),
		("bool", "shift"),
		("slot", "slot_data")),
	#Set slot
	0x67: (
		("byte", "window_id"),
		("short", "slot"),
		("slot", "slot_data")),
	#Window items
	0x68: (
		("byte", "window_id"),
		("short", "data_size")),
	#Update progress bar
	0x69: (
		("byte", "window_id"),
		("short", "progress_bar_type"),
		("short", "progress")),
	#Transaction
	0x6A: (
		("byte", "window_id"),
		("short", "transaction_id"),
		("bool", "accepted")),
	# Creative Inventory Action
	0x6B: (
		("short", "slot"),
		("slot", "slot_data")),
	# Enchant Item
	0x6C: (
		("byte", "window_id"),
		("byte", "enchantment")),
	#Update sign
	0x82: (
		("int", "x"),
		("short", "y"),
		("int", "z"),
		("string16", "line_1"),
		("string16", "line_2"),
		("string16", "line_3"),
		("string16", "line_4")),
	#Map data
	0x83: (
		("short", "unknown1"),
		("short", "map_id"),
		("ubyte", "data_size")),
	#Update Tile Entity
	0x84: (
		("int", "x"),
		("short", "y"),
		("int", "z"),
		("byte", "action"),
		("int", "custom1"),
		("int", "custom2"),
		("int", "custom3")),
	#Increment statistic
	0xC8: (
		("int", "statistic_id"),
		("byte", "amount")),
	# Player List Item
	0xC9: (
		("string16", "player_name"),
		("bool", "online"),
		("short", "ping")),
	#Server list ping
	0xFE: (),
	#Disconnect
	0xFF: ("string16", "reason")}


class PacketDecoder:
	def __init__(self, to_server):
		self.buff = ''
		self.error_count = 0
		self.node = CLIENT_TO_SERVER if to_server else SERVER_TO_CLIENT
		self.iPacketCounter = 0


	def get_struct(self, packet):
		"""Reads ident and direction from packet, and returns the associated struct description from structs global.
		Normalises return to be a ((str, str), ...)"""
		o = structs[packet.ident]
		if isinstance(o, dict):
			o = o[packet.direction]
		if len(o) and not isinstance(o[0], tuple):
			o = (o),
		return o


	def pack(self, data_type, data):
		if data_type in data_types:
			format = data_types[data_type]
			return self.pack_real(format[0], data)
		
		if data_type == "string8": return self.pack("short", len(data)) + data
		if data_type == "string16": return self.pack("short", len(data)) + data.encode('utf-16be')
		if data_type == "slot":
			o = self.pack('short', data['id'])
			if data['id'] > 0:
				o += self.pack('byte',  data['amount'])
				o += self.pack('short', data['damage'])
			if 'extra' in data:
				nbtdata = data['extra']
				if nbtdata is None:
					o += self.pack('short', -1)
				else:
					nbt_len = len(nbtdata)
					o += self.pack('short', nbt_len)
					o += nbtdata
			return o
		if data_type == "metadata":
			o = ''
			for mtype, val in data:
				mtype2 = mtype >> 5
				o += self.pack('byte', mtype)
				if mtype2 == 0: o += self.pack('byte', val) 
				if mtype2 == 1: o += self.pack('short', val) 
				if mtype2 == 2: o += self.pack('int', val) 
				if mtype2 == 3: o += self.pack('float', val) 
				if mtype2 == 4: o += self.pack('string16', val)
				if mtype2 == 5:
					o += self.pack('short', val['id'])
					o += self.pack('byte',  val['count'])
					o += self.pack('short', val['damage'])
				if mtype2 == 6:
					for i in range(3):
						o += self.pack('int', val[i])
			o += self.pack('byte', 127)
			return o


	def unpack(self, data_type):
		"""Reads buff (consuming bytes) and returns the unpacked value according to the given type."""
		if data_type in data_types:
			format = data_types[data_type]
			return self.unpack_real(format[0], format[1])
		
		if data_type == "string8":
			length = self.unpack('short')
			if length < 0:
				raise Exception("Negative length for string")
			if len(self.buff) < length:
				raise IncompleteData()
			string = self.buff[:length]
			self.buff = self.buff[length:]
			return string
		if data_type == "string16":
			length = self.unpack('short')
			if length < 0:
				raise Exception("Negative length for string")
			if len(self.buff) < 2*length:
				raise IncompleteData()
			string = self.buff[:2*length].decode('utf-16be')
			self.buff = self.buff[2*length:]
			return string
		if data_type == "slot":
			o = {}
			o["id"] = self.unpack('short')
			if o["id"] > 0:
				o["amount"] = self.unpack('byte')
				o["damage"] = self.unpack('short')
			if o["id"] in SLOT_EXTRA_DATA_IDS:
				extra_len = self.unpack('short')
				if extra_len <= 0:
					o["extra"] = None
				else:
					if len(self.buff) < extra_len:
						raise IncompleteData()
					extra_buff = self.buff[:extra_len]
					self.buff = self.buff[extra_len:]
					o["extra"] = extra_buff
			return o
		if data_type == "metadata":
			#[(17, 0), (0, 0), (16, -1)]
			o = []
			mtype = self.unpack('byte')
			while mtype != 127:
				mtype2 = mtype >> 5
				t = 0
				if mtype2 == 0: t = self.unpack('byte') 
				if mtype2 == 1: t = self.unpack('short') 
				if mtype2 == 2: t = self.unpack('int') 
				if mtype2 == 3: t = self.unpack('float') 
				if mtype2 == 4: t = self.unpack('string16')
				if mtype2 == 5:
					t = {}
					t["id"] = self.unpack('short')
					t["count"] = self.unpack('byte')
					t["damage"] = self.unpack('short')
				if mtype2 == 6:
					t = []
					for i in range(3):
						s = self.unpack('int')
						t.append(s)
				t = (mtype, t)
				o.append(t)
				mtype = self.unpack('byte')
			return o

					
	def unpack_real(self, data_type, length):
		"""A helper function for unpack(), it handles any data type that is understood by the struct module."""
		if len(self.buff) < length:
			raise IncompleteData()
		o = struct.unpack_from('!'+data_type, self.buff)[0]
		self.buff = self.buff[length:]
		return o


	def pack_real(self, data_type, data):
		return struct.pack('!'+data_type, data)


	def unpack_array(self, data_type, count):
		a = []
		for i in range(count):
			a.append(self.unpack(data_type))
		return a


	def pack_array(self, data_type, data):
		o = ''
		for d in data:
			o += self.pack(data_type, d)
		return o
	def unpack_array_fast(self, data_type, count):
		data_type = data_types[data_type]
		if len(self.buff) < count*data_type[1]:
			raise IncompleteData()
		o = struct.unpack_from(data_type[0]*count, self.buff)
		self.buff = self.buff[count*data_type[1]:]
		return o
		
	def pack_array_fast(self, data_type, data):
		data_type = data_types[data_type]
		return struct.pack(data_type[0]*len(data), *data)


	def read_packet(self):
		"""Reads the bytestring in self.buff, and returns the first packet contained within it.
		Sets self.buff to remaining bytestring.

		If packet is incomplete, returns None. But may raise if it thinks a real malformed packet has been recieved.
		"""

		#self.debug("READ BUFFER SIZE: %d" % len(self.buff))
		backup = self.buff[:]
		packet = Packet()
		try:
			packet.direction = self.node
			packet.ident = self.unpack('ubyte')
			
			#Defined structs from huge dict
			for datatype, name in self.get_struct(packet):
				# this populates packet.data with {name: value}
				packet.data[name] = self.unpack(datatype)

			# I believe the following are packet-type specific fixes for variable-length packets.

			#0x17
			if packet.ident == 0x17:
				if packet.data['unknown'] > 0:
					packet.data['x2'] = self.unpack('short')
					packet.data['y2'] = self.unpack('short')
					packet.data['z2'] = self.unpack('short')
		
			#0x33
			if packet.ident in (0x33, 0x34):
				packet.data['data'] = self.unpack_array_fast('byte', packet.data['data_size'])
				del packet.data["data_size"]
		
#			#0x34
#			if packet.ident == 0x34:
#				coords = self.unpack_array_fast('short', packet.data['data_size'])
#				btype = self.unpack_array_fast('byte',  packet.data['data_size'])
#				metadata = self.unpack_array_fast('byte',  packet.data['data_size'])
#				packet.data["blocks"] = []
#				for i in zip(coords, btype, metadata):
#					block = {}
#					block["x"] =		i[0] >> 12
#					block["z"] = 0x0F & i[0] >> 8
#					block["y"] = 0xFF & i[0]
#					block["type"] = i[1]
#					block["metadata"] = i[2]
#					packet.data["blocks"].append(block)
#				del packet.data["data_size"]
		
			#0x3C
			if packet.ident == 0x3C:
				records = self.unpack_array_fast('byte', packet.data['data_size']*3)
				i = 0
				packet.data["blocks"] = []
				while i < packet.data['data_size']*3:
					packet.data["blocks"].append(dict(zip(('x','y','z'), records[i:i+3])))
					i+=3
				del packet.data["data_size"]
		
			#0x68
			if packet.ident == 0x68:
				packet.data["slots_data"] = self.unpack_array('slot', packet.data["data_size"])
				del packet.data["data_size"]
			#0x82:
			if packet.ident == 0x82:
				packet.data["text"] = []
				for i in range(4):
					packet.data["text"].append(packet.data["line_%s" % (i+1)])
					
			#0x83
			if packet.ident == 0x83:
				packet.data["data"] = self.unpack_array_fast('byte', packet.data['data_size'])
				del packet.data["data_size"]

			# Sets packet.original to the byte string that the packet was decoded from.
			packet.original = backup[:len(backup) - len(self.buff)]

			return packet

		except IncompleteData:
			self.buff = backup
			return None
		except Exception, ex:
			self.buff = backup
			ex.args += (self.buff[20:],)
			raise


	def encode_packet(self, packet):
		"""Takes a packet, and returns the encoded bytestring representing it."""

		try:
			output = self.pack('ubyte', packet.ident)
			append = ''
			#0x17
			if packet.ident == 0x17:
				if packet.data['unknown'] > 0:
					for i in ('x2','y2','z2'):
						append += self.pack('short', packet.data[i])
			#0x33
			if packet.ident == 0x33:
				packet.data['data_size'] = len(packet.data['data'])
				append += self.pack_array_fast('byte', packet.data['data'])
			
			#0x34
			if packet.ident == 0x34:
				coords = []
				btypes = []
				metadata = []
				for i in packet.data['blocks']:
					coords.append(i['x'] << 12 | i['z'] << 8 | i['y'])
					btypes.append(i['type'])
					metadata.append(i['metadata'])
				
				packet.data['data_size'] = len(coords)
				append += self.pack_array_fast('short', coords)
				append += self.pack_array_fast('byte', btypes)
				append += self.pack_array_fast('byte', metadata)
			
			#0x3C
			if packet.ident == 0x3C:
				array = []
				for i in packet.data['blocks']:
					array += [i['x'], i['y'], i['z']]
				packet.data['data_size'] = len(packet.data['blocks'])
				append += self.pack_array_fast('byte', array)
			
			#0x68
			if packet.ident == 0x68:
				packet.data['data_size'] = len(packet.data['slots_data'])
				append += self.pack_array('slot', packet.data['slots_data'])
			#0x82: Sign
			if packet.ident == 0x82:
				for i in range(4):
					packet.data["line_%s" % (i+1)] = packet.data["text"][i]
			#0x83
			if packet.ident == 0x83:
				packet.data['data_size'] = len(packet.data['data'])
				append += self.pack_array_fast('byte', packet.data['data'])
		
			for i in self.get_struct(packet):
				output += self.pack(i[0], packet.data[i[1]])
			
			output += append
			return output
		except:
			raise


def stateless_unpack(buff, to_server):
	"""A wrapper about the normal objects, that lets you unpack encoded packets easily.
	Returns (packet, remaining_buff), where remaining_buff is the given buffer without the bytes eaten by the packet.
	If no more packets can be read from buff, returns (None, buff).
	"""
	decoder = PacketDecoder(to_server)
	decoder.buff = buff
	packet = decoder.read_packet()
	return packet, decoder.buff

def stateless_pack(packet, to_server):
	"""A wrapper about the normal objects, that lets you pack decoded packets easily.
	Returns the bytestring that represents the packet."""
	decoder = PacketDecoder(to_server)
	return decoder.encode_packet(packet)

class IncompleteData(Exception):
	pass
