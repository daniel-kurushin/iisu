from object.bins_collection.data \
	import Data
	
from utilities.unpack \
	import unpack
	
	
	
	
	
	
	
def parse_packet_70h(packet_bytes, data_mask):
	if len(packet_bytes) != 52:
		raise Exception("Некорректная длина пакета") #!!!!!
		
		
	data = Data(data_mask)
	
	data.acceleration = \
		unpack("<f", packet_bytes[4:8]), \
			unpack("<f", packet_bytes[8:12]), \
			unpack("<f", packet_bytes[12:16])
			
	data.angular_velocity = \
		unpack("<f", packet_bytes[16:20]), \
			unpack("<f", packet_bytes[20:24]), \
			unpack("<f", packet_bytes[24:28])
			
	data.orientation = \
		unpack("<f", packet_bytes[32:36]), \
			unpack("<f", packet_bytes[28:32]), \
			unpack("<f", packet_bytes[36:40])
			
	data.position = \
		unpack("<i", packet_bytes[40:44]) / 10 ** 8, \
			unpack("<i", packet_bytes[44:48]) / 10 ** 8, \
			unpack("<f", packet_bytes[48:52])
			
			
	return data
	