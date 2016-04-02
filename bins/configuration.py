PORTS	 = ['/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3']
TIMEOUT  = 3
BAUDRATE = 460800
PARITY   = "N"
STOPBITS = 1
BYTESIZE = 8

SYNCHRO  = b'\xAA'
MAX_PACKET_LENGTH = 100

packets_out = dict(
	p40h = {
		'Type':		[ 1,'>b',1,None],
		'PkID':		[ 2,'>b',1,None],
		'Freq':		[ 3,'>f',1,None],
	},

	p45h = {
		'Lat_0':	[ 1,'>i',10 ** 8,None],
		'Lon_0':	[ 2,'>i',10 ** 8,None],
		'H_0':		[ 3,'>i',1,None],
		'A_0':		[ 4,'>i',1,None],
		'cmd':		[ 5,'>i',1,None,{
				'SNS_lat_lon':		2,
				'SNS_A_lat_lon,': 	3,
				'ODM_calib':		10,
				'OP_lat_lon_H':		13,
			}],
	},

	p4Fh = {
		'LFT_WHL':	[ 1,'>f',1,None],
		'RGT_WHL':	[ 2,'>f',1,None],
		'A_optical':[ 3,'>f',1,None],
		'SKO_A':	[ 4,'>f',1,None]
	},

	p53h = {
		'K_odm':	[ 1,'>f',1,None],
		'Psi':		[ 2,'>f',1,None],
		'Tetta':	[ 3,'>f',1,None],
		'Gamma':	[ 4,'>f',1,None],
		'D_bins':	[ 5,'>f',1,None],
		'ust_f':	[ 6,'>i',1,None],
		'R1':		[ 7,'>f',1,None],
		'R2':		[ 8,'>f',1,None],
		'R3':		[ 9,'>f',1,None],
	}
)
packets_in = dict(
	p33h = {
		'V_e':		( 1,'<f',1),
		'V_n':		( 2,'<f',1),
		'V_h':		( 3,'<f',1),
		'V_g':		( 4,'<f',1),
		'A_sns':	( 5,'<f',1),
		'H_sns':	( 6,'<f',1),
		'HDOP':		( 7,'<f',1),
		'VDOP':		( 8,'<f',1),
		'T_gr':		( 9,'<f',1),
		'Q'	:		(10,'<f',1),
		'fRMS':		(11,'<f',1),
		'fGGA':		(12,'<f',1),
		'fGSA':		(13,'<f',1),
		'Lat_sns':	(14,'<i',1 / 10 ** 8),
		'Lon_sns':	(15,'<i',1 / 10 ** 8),
		'R1':		(16,'<f',1),
		'R2':		(17,'<f',1),
		'R3':		(18,'<f',1),
	},

	p35h = {
		'S_full':	( 1,'<f',1),
		'V_g':	( 2,'<f',1),
		'Ve':		( 3,'<f',1),
		'Vn':		( 4,'<f',1),
		'Vh':		( 5,'<f',1),
		'K_odm':	( 6,'<f',1),
		'Psi':		( 7,'<f',1),
		'Tetta':	( 8,'<f',1),
		'Lat_err':	( 9,'<f',1),
		'Lon_err':	(10,'<f',1),
		'H_err':	(11,'<f',1),
		'Psi_aprx':	(12,'<f',1),
		'Tetta_aprx':(13,'<f',1),
		'K_odm_aprx':(14,'<f',1),
		'Psi_calc':	(15,'<f',1),
		'Tetta_calc':(16,'<f',1),
		'K_odm_calc':(17,'<f',1),
	},

	p70h = {
		'state':	( 1,'<i',1),
		'A_x':		( 2,'<f',1),
		'A_y':		( 3,'<f',1),
		'A_z':		( 4,'<f',1),
		'W_x':		( 5,'<f',1),
		'W_y':		( 6,'<f',1),
		'W_z':		( 7,'<f',1),
		'C_bins':	( 8,'<f',1),
		'A_bins':	( 9,'<f',1),
		'B_bins':	(10,'<f',1),
		'Lat_bins':	(11,'<i',1 / 10 ** 8),
		'Lon_bins':	(12,'<i',1 / 10 ** 8),
		'H_bins':	(13,'<f',1),
	},

	p8Eh = {
		'P': 		( 1,'<f',1),
		'T': 		( 2,'<f',1),
	},

	pDEh = {
		'X_bins':	( 1,'<f', 1),
		'Y_bins':	( 2,'<f', 1),
		'Z_bins':	( 3,'<f', 1),
		'X_sns':	( 4,'<f', 1),
		'Y_sns':	( 5,'<f', 1),
		'Z_sns':	( 6,'<f', 1),
		'dX':		( 7,'<f', 1),
		'dY':		( 8,'<f', 1),
		'dZ':		( 9,'<f', 1),
	},
)
