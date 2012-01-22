
def on_start():
	pass

def on_packet(packet, user, to_server):
	if packet.name() == 'Handshake':
		user.username = packet.data['username']
	return packet
