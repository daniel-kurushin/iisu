from object.bins_collection.packets.crc \
	import compute_crc
	
def send_packet(bins_serial, packet_id, data):
	# return #!!!!!
	if not 0 <= packet_id <= 255:
		raise Exception() #!!!!!
		

    len_pack = len(data)*4 + 3

	request = packet_id.to_bytes(length = 1, byteorder = "little")

    for elem in data:
        if type(elem) == float:
            request += \
                struct.pack('<f', elem)
        elif type(elem) == int:
            request += \
                struct.pack('<i', elem)
        else:
            pass
	crc = compute_crc(request)
	
	request  = b"\xAA\xAA" + len_pack.to_bytes(length = 1, byteorder = "little") + request
	request += crc.to_bytes(length = 2, byteorder = "little")
		
		
	bins_serial.write(request)

