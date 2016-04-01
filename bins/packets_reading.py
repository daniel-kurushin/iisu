from object.bins_collection.data \
	import Data
	
from object.bins_collection.packets.crc \
	import compute_crc
	
from object.bins_collection.packets.packet_33h_parsing \
	import parse_packet_33h
	
from object.bins_collection.packets.packet_70h_parsing \
	import parse_packet_70h
	
from utilities.communication.timer \
	import start_timer
	
import asyncio







SYNCHRONIZATION_SIGNAL  = 0xAA
SYNCHRONIZATIONS_NUMBER = 2







@asyncio.coroutine
def read_packet(bins_serial, data_mask):
	# import random
	# yield from asyncio.sleep(0.5)
	# data = Data(data_mask)
	# data.acceleration = [random.randint(0, 9) / 10] * 3
	# data.angular_velocity = [random.randint(0, 9) / 10] * 3
	# data.orientation = [random.randint(0, 9) / 10] * 3
	# data.position = [random.randint(0, 9) / 10] * 3
	# return data
	def read(bytes_number):
		#!!!!! В целях отладки. Потом убрать ветку else
		if bins_serial is not None:
			bytes = bins_serial.read(bytes_number)
		else:
			import time
			time.sleep(0.1)
			bytes = b"\xAA" * bytes_number
			
		return bytes
		
		
	def read_int(bytes_number):
		bytes = read(bytes_number)
		value = int.from_bytes(bytes, byteorder = "little")
		
		return value, bytes
		
		
		
	try:
		synchronizations_number = 0
		
		while synchronizations_number != SYNCHRONIZATIONS_NUMBER:
			signal, _ = read_int(1)
			
			if signal == SYNCHRONIZATION_SIGNAL:
				synchronizations_number += 1
			else:
				synchronizations_number = 0
				
				
				
		yield
		packet_length, _  = read_int(1)
		packet_length    -= 3
		
		if packet_length < 0:
			raise Exception() #!!!!!
			
			
		packet_id, packet_id_bytes = read_int(1)
		packet_data                = read(packet_length)
		packet_crc, _              = read_int(2)
		
		
		packet       = packet_id_bytes + packet_data
		computed_crc = compute_crc(packet)
		
		if packet_crc != computed_crc:
			raise Exception() #!!!!!
			
			
			
		if packet_id == 0x33:
			try:
				data = parse_packet_33h(packet_data, data_mask)
			except:
				raise
		elif packet_id == 0x70:
			try:
				data = parse_packet_70h(packet_data, data_mask)
			except:
				raise
		else:
			data = Data(data_mask)
			
			
			
		return data
	except:
		raise
		