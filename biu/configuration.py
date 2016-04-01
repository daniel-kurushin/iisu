PORTS	 = ['/dev/ttyUSB3','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB0']
TIMEOUT  = 3
BAUDRATE = 9600

BIU_QUERY= dict(
	khc = dict(q = b'\xae\xae\x01\x00\xff\x07\x00', a =   10),
	kru = dict(q = b'\xae\xae\x02\x00\xff\x07\x00', a =   15),
	ken = dict(q = b'\xae\xae\x03\x00\xff\x07\x00', a = None),
	kst = dict(q = b'\xae\xae\x04\x00\xff\x07\x00', a = None),
)
