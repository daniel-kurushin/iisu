import sys
import datetime
import json
import math

from struct import pack, unpack
from serial import Serial, SerialException
from threading import Thread
from time import sleep


try:
	import bins.configuration as configuration
	from bins.crc import compute_crc
except ImportError:
	import configuration as configuration
	from crc import compute_crc

D33 = dict(
	signature = (b'\x53', b'\x33'),
)

D35 = dict(
	signature = (b'\x47', b'\x35'),
)

D70 = dict(
	signature = (b'\x37', b'\x70'),
	state = 0,
)

D72 = dict(
	signature = (b'\x33', b'\x72'),
)

D85 = dict(
	signature = (b'\xa3', b'\x85'),
)

D8E = dict(
	signature = (b'\x0b', b'\x8e'),
)

DDE = dict(
	signature = (b'\x27', b'\xde'),
)

class BINS(Serial):
	NAME = 'BINS'

	MAX_ERROR_COUNT = 100

	state = dict(
		errorcount = 0,
	)

	def get_state(self):
		print 
		self.state.update(D70)
		self.state.pop('signature')
		return self.state

	def read_synchro(self):
		if self.read() == configuration.SYNCHRO:
			if self.read() == configuration.SYNCHRO:
				return True
		return False

	def read_signature(self):
		return self.read(), self.read()


	def ask_packet(self, packet_id = 0x70, packet_frequency = 10):
		x = configuration.packets_out[0x40]
		x['PkID'][3] = packet_id 
		x['Freq'][3] = packet_frequency // 10
		x = self.send_packet(0x40,self.make_packet(x))
		return x


	def get_my_port(self, open_ports = []):
		ports = configuration.PORTS
		for port in open_ports:
			ports.remove(port)
		for p in ports:
			try:
				print('Trying port %s ... ' % p, end = '', file = sys.stderr)
				s = Serial(port = p, baudrate = configuration.BAUDRATE, timeout = 0.5)
				n = 0
				while 1:
					if s.read() == configuration.SYNCHRO:
						if s.read() == configuration.SYNCHRO:
							print('success!', file = sys.stderr)
							return p
					elif s.read() == b'':
						raise SerialException('Empty data on port %s' % p)
					else: n += 1
					if n > configuration.MAX_PACKET_LENGTH:
						raise SerialException('Wrong data on port %s' % p)
			except SerialException as e:
				print(e, file = sys.stderr)
		return None

	def list_packets(self, n = 0):
		res = {}
		while n > 0:
			if self.read_synchro():
				pln, sig = self.read_signature()
				res.update({hex(ord(sig)):{'present': True, 'len': ord(pln)}})
				n -= 1

		return res

	def send_packet(self, packet_id, data):
		# return #!!!!!
		if not 0 <= packet_id <= 255:
			raise Exception() #!!!!!
		
		to_send = \
			pack('>B', packet_id) + \
			b''.join(data)

		crc = compute_crc(to_send)
		to_send = \
			configuration.SYNCHRO + \
			configuration.SYNCHRO + \
			pack('>B', (len(to_send) + 2)) + \
			to_send + \
			pack('<H', crc)

		# "\x64\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
			# AA AA 17 45 40 A3 08 06 CD C3 D9 05 B4 00 00 00 64 00 00 00 05 00 00 00 F5 8D
		# b'\xaa\xaa\x0b@p\x00\x00\x00\x00\x00\x00\x00\xd5\xef'
		#     aa  aa  08
		# aa aa 07 4d 00 00 00 00 12 30
		# AA AA 07 4D 00 00 61 45 68 10
		# aa aa 06 40 01 01 3f 80 00 00 f1 40 
		print(''.join(["%02x " % x for x in to_send]), file = sys.stderr)
		return self.write(to_send)


	def make_packet(self, packet_data = {}):
		ordered = [0] * len(packet_data.keys())
		for key, val in packet_data.items():
			n = val[0] - 1
			F = val[1]
			K = val[2]
			D = val[3]
			ordered[n] = pack(F, D * K)

		return ordered
	
	def parse_packet(self, packet_id, packet_bytes):
		def parse_state(to_parse, dict_to_fill):
			_ = unpack('<I', to_parse)[0]
			out = {}
			for n in range(len(dict_to_fill)):
				out.update({dict_to_fill[n]: _ & 1})
				n += 1
				_ = _ >> 1

			# some BINS magic!
			out['ins_ok'] = not out['ins_ok']
			out['sns_ok'] = not out['sns_ok']
			out['mk_ok'] = not out['mk_ok']
			out['dvs_good'] = not out['dvs_good']
			out['bv_ok'] = not out['bv_ok']
			out['obj_move'] = not out['obj_move']
			out['dbl_hyr'] = not out['dbl_hyr']
			out['dbl_hyr_rpt'] = not out['dbl_hyr_rpt']
			out['acc_crr'] = not out['acc_crr']
			out['odo_crr'] = not out['odo_crr']
			return out

		data = {}
		for key, val in configuration.packets_in[packet_id].items():
			F = val[1]
			L = len(pack(F,0))
			d0, d1 = (val[0] - 1) * L, (val[0] - 1) * L + L
			K = val[2]
			if packet_id == 0x70 and key == 'state':
				data[key] = parse_state(packet_bytes[d0:d1], val[3])
			else:
				data[key] = unpack(F, packet_bytes[d0:d1])[0] * K
		return data

	def read_packets(self):
		print('start reading', file = sys.stderr)
		while not self.end and \
			self.state['errorcount'] < self.MAX_ERROR_COUNT:


			if self.read_synchro():
				pln, sig = self.read_signature()
				if (pln, sig) == D70['signature']: 
					D70.update(self.parse_packet(0x70,self.read(ord(pln))))
				elif (pln, sig) == D72['signature']: 
					D72.update(self.parse_packet(0x72,self.read(ord(pln))))
				elif (pln, sig) == D33['signature']: 
					D33.update(self.parse_packet(0x33,self.read(ord(pln))))
				elif (pln, sig) == D35['signature']: 
					D35.update(self.parse_packet(0x35,self.read(ord(pln))))
				elif (pln, sig) == D8E['signature']: 
					D8E.update(self.parse_packet(0x8E,self.read(ord(pln))))
				elif (pln, sig) == D85['signature']: 
					D85.update(self.parse_packet(0x85,self.read(ord(pln))))
				elif sig == 0:
					self.state


		print('stop reading', file = sys.stderr)

	def stop(self):
		self.end = True
		self.reader.join()


	def __init__(self, open_ports = []):
		try:
			super().__init__(
				port     = self.get_my_port(open_ports),
				timeout  = configuration.TIMEOUT,
				baudrate = configuration.BAUDRATE,
				parity   = configuration.PARITY,
				stopbits = configuration.STOPBITS,
				bytesize = configuration.BYTESIZE,
			)

			self.end = False

			self.state.update(self.list_packets(20))
			self.ask_packet(0x33,100)
			self.ask_packet(0x85,100)
			self.ask_packet(0x70,100)
			print(self.list_packets(20), file = sys.stderr)
			self.reader = Thread(target = self.read_packets)
			self.reader.start()
			while D70['state'] == 0:
				sleep(0.1)
			self.state.update(D70)

		except Exception as e:
			raise e

if __name__ == "__main__":
	bins = BINS()
	while 1:
		try:
			sleep(1)
			print(D70['A_bins'],D70['B_bins'],D70['C_bins'])
		except:
			break
	bins.stop()



	# x = configuration.packets_out[0x76]
	# x['rot_A'][3] = -90.000
	# x['rot_B'][3] = 0 #  10.823
	# x['rot_C'][3] = 0 #-178.980
	# y = bins.make_packet(x)
	# z = bins.send_packet(0x76,y)
	# sleep(1)
	# print(D85['K13'],D85['K14'],D85['K15'])
	# print(D70['A_bins'],D70['B_bins'],D70['C_bins'])

	# x = configuration.packets_out[0x76]
	# x['rot_A'][3] = -90
	# x['rot_C'][3] = -10.823
	# x['rot_B'][3] = 0 #-178.980
	# y = bins.make_packet(x)
	# z = bins.send_packet(0x76,y)
	# sleep(1)
	# print(D85['K13'],D85['K14'],D85['K15'])
	# print(D70['A_bins'],D70['B_bins'],D70['C_bins'])

	# x = configuration.packets_out[0x76]
	# x['rot_A'][3] = -90
	# x['rot_C'][3] = -10.823
	# x['rot_B'][3] = -179
	# y = bins.make_packet(x)
	# z = bins.send_packet(0x76,y)
	# sleep(1)
