from object.bins_collection.data \
	import Data
	
from utilities.unpack \
	import unpack
	
	
	
	
	
	
	
def _______parse_packet_33h(packet_bytes, data_mask):
	if len(packet_bytes) != 75 and len(packet_bytes) != 72 and len(packet_bytes) != 80:
		raise Exception("Некорректная длина пакета") #!!!!!
		
		
	data = Data(data_mask)
	
	data.sns_position = \
		[float(unpack("<i", packet_bytes[i:i+4]) / 10 ** 8) for i \
			in range(0, len(packet_bytes), 4)]
	data.sns_position = list(data.sns_position)+[str(packet_bytes)]
		# float(unpack("<i", packet_bytes[52:56]) / 10 ** 8), \
			# float(unpack("<i", packet_bytes[56:60]) / 10 ** 8)
			
			
	return data


def parse_packet_33h(packet_bytes, data_mask):
	if len(packet_bytes) != 80:
		raise Exception("Некорректная длина пакета") #!!!!!


	data = Data(data_mask)

	data.sns_position = \
		unpack("<i", packet_bytes[52:55]) / 10 ** 8, \
			unpack("<i", packet_bytes[56:59]) / 10 ** 8

    data.speed = \
        unpack("<f", packet_bytes[0:3]), \
			unpack("<f", packet_bytes[4:7]), \
			unpack("<f", packet_bytes[8:11])

	data.dop = \
		unpack("<f", packet_bytes[24:27]), \
			unpack("<f", packet_bytes[28:31])

	return data