"""This plugin will reencode packets back to bytestring and ensure they match their original, if any.
Note this is a lengthy operation and should be used sparingly."""

import packet_decoder

def on_start():
	pass

def on_packet(packet, user, to_server):
	if hasattr(packet, 'original'):
		reencoded = packet_decoder.stateless_pack(packet, to_server)
		if packet.original != reencoded:
			raise Exception("Packet (%s) changed: Reencodes to %s, not %s" % (packet, repr(reencoded), repr(packet.original)))
		return packet
