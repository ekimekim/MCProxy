
def on_start():
	pass

def on_packet(packet, user, to_server):
	if to_server and packet.name() == 'Handshake':
		parts = packet.data['username'].split(';')
		user.username = ';'.join(parts[:-1]).lower()
	return packet
