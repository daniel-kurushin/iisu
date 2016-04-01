from object.bins_collection.packets.crc \
	import compute_crc
	
	
def ask_packet(bins_serial, packet_id, packet_frequency):
	# return #!!!!!
	if not 0 <= packet_id <= 255:
		raise Exception() #!!!!!
		
	if not 0 <= packet_frequency <= 1000:
		raise Exception() #!!!!!
		
		
	request  = b"\x40"
	request += packet_id.to_bytes(length = 1, byteorder = "little")
	request += \
		(packet_frequency // 10).to_bytes(
			length    = 4,
			byteorder = "little",
		)
	crc = compute_crc(request)
	
	request  = b"\xAA\xAA\x08" + request
	request += crc.to_bytes(length = 2, byteorder = "little")
		
		
	bins_serial.write(request)


def ask_packet_new(bins_serial, type_of_protocol, packet_id, packet_frequency):
	# return #!!!!!
	if not 0 <= packet_id <= 255:
		raise Exception() #!!!!!

	if not 0 <= packet_frequency <= 1000:
		raise Exception() #!!!!!


	request  = b"\x40"
    request += type_of_protocol.to_bytes(length = 1, byteorder = "little")
	request += packet_id.to_bytes(length = 1, byteorder = "little")
	request += \
		(packet_frequency // 10).to_bytes(
			length    = 4,
			byteorder = "little",
		)
	crc = compute_crc(request)

	request  = b"\xAA\xAA\x09" + request
	request += crc.to_bytes(length = 2, byteorder = "little")


	bins_serial.write(request)