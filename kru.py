from tkinter import *
from urllib.request import urlopen
from json import loads, dumps

MAX_SPD = 35

url_prefix = 'http://192.168.0.101:8000'

cmd_engine_stop          = '/engine/stop'
cmd_move_set_acc_steer	 = '/move/set_acc_steer'
prm_move_set_acc_steer	 = "req_acc_pos=%i&rgt_brk=%i&lgt_brk=%i&req_str_pos=%i"
cmd_get_state	         = '/state'
cmd_get_distances		 = '/state/distances'
cmd_get_accpos			 = '/engine/get_pos'
cmd_get_strpos			 = '/steer/get_pos'
cmd_get_power			 = '/power/measure'
cmd_get_orientation	     = '/orientation/get'

class Chasis(object):
	def get_state(self, event):
		_ = {}
		_.update(get_json_url_to_dict(cmd_get_accpos))
		_.update(get_json_url_to_dict(cmd_get_strpos))
		_.update(get_json_url_to_dict(cmd_get_orientation))
		u12v = 0 # _['U_12']
		i12v = 0 # _['I_12']
		i48v = 0 # _['I_48']
		stp  = _['pos']
		acc  = _['currentAccelPos']
		azm  = _['A_bins'] - 180
		return i48v, i12v, u12v, azm, stp, acc

	def more(self, event = None):
		_ = req_acc_pos.get()
		if _ < 30: 
			_ = 31
		elif _ < 35: 
			_ += 1
		else:
			_ = 35
		req_acc_pos.set(_)

	def less(self, event = None):
		_ = req_acc_pos.get()
		if -30 < _ :
			_ = -31
		elif -35 < _ :
			_ -= 1
		else:
			_ = -35
		req_acc_pos.set(_)

	def left(self, event = None):
		_ = req_str_pos.get()
		if -20 < _ :
			_ -= 5
		req_str_pos.set(_)

	def right(self, event = None):
		_ = req_str_pos.get()
		if _ < 20:
			_ += 5
		req_str_pos.set(_)

	def lbrake(self, event = None):

		pass

	def rbrake(self, event = None):

		pass

	def lflick(self, event = None):
		pass

	def noflick(self, event = None):
		pass

	def rflick(self, event = None):
		pass

	def stop(self, event = None):
		res = get_json_url_to_dict(cmd_engine_stop)
		req_acc_pos.set(0)
		req_str_pos.set(0)
		return res

	def get_front_distance(self):
		fr = get_json_url_to_dict(cmd_get_distances)['front']
		return fr


class CV(object):

	def left(self, event = None):

		pass

	def right(self, event = None):

		pass

	def up(self, event = None):

		pass

	def down(self, event = None):

		pass

	def center(self, event = None):

		pass

	def picture(self, event = None):

		pass

def build_frameset(x):
	header  = Frame(x, bd = 1)
	footer  = Frame(x, bd = 1, bg = 'blue')
	pleft   = Frame(x, bd = 1)
	pcenter = Frame(x, bd = 1)
	pright  = Frame(x, bd = 1)
	header.grid( row=0, column=0, sticky="nwse", columnspan=3)
	footer.grid( row=2, column=0, sticky="nwse", columnspan=3)
	pleft.grid(  row=1, column=0, sticky="nwse")
	pcenter.grid(row=1, column=1, sticky="nwse")
	pright.grid( row=1, column=2, sticky="nwse")
	x.columnconfigure(1, weight = 1)
	x.rowconfigure(1, weight = 1)
	return header,footer,pleft,pcenter,pright

def build_header(h):
	Label(h, text = 'Ping'    ).grid(row = 0, column = 0)
	Label(h, text = 'Скорость').grid(row = 0, column = 1)
	Label(h, text = 'Руль'    ).grid(row = 0, column = 2)
	Label(h, text = 'Азимут'  ).grid(row = 0, column = 3)
	Label(h, text = 'U 12V'   ).grid(row = 0, column = 4)
	Label(h, text = 'I 12V'   ).grid(row = 0, column = 5)
	Label(h, text = 'I 48V'   ).grid(row = 0, column = 6)
	PNG  = IntVar()
	_ = Checkbutton(h, variable = PNG)
	SPD  = Scale(h, orient = HORIZONTAL, from_ = -MAX_SPD, to = MAX_SPD)
	STP  = Scale(h, orient = HORIZONTAL, from_ =      -19, to =      19)
	AZM  = Scale(h, orient = HORIZONTAL, from_ =     -180, to =     180)
	U12V = Scale(h, orient = HORIZONTAL, from_ =        0, to =      15)
	I12V = Scale(h, orient = HORIZONTAL, from_ =        0, to =      10)
	I48V = Scale(h, orient = HORIZONTAL, from_ =        0, to =      20)
	col = 0
	for _ in [_,SPD,STP,AZM,U12V,I12V,I48V]:
		_.grid(row=1,column=col)
		col += 1
	return PNG, SPD, STP, AZM, U12V, I12V, I48V

def build_left_frame(x):
	Button(x, text='⮉', command = chasis.more   ).grid(row=0,column=0,columnspan=5, sticky="nwse")
	Button(x, text='⮋', command = chasis.less   ).grid(row=2,column=1,columnspan=3, sticky="nwse")
	Button(x, text='⮈', command = chasis.left   ).grid(row=1,column=1,columnspan=1, sticky="nwse")
	Button(x, text='⮊', command = chasis.right  ).grid(row=1,column=3,columnspan=1, sticky="nwse")
	Button(x, text='⏮', command = chasis.lbrake ).grid(row=2,column=0,columnspan=1, sticky="nwse")
	Button(x, text='⏭', command = chasis.rbrake ).grid(row=2,column=4,columnspan=1, sticky="nwse")
	Button(x, text='⮪', command = chasis.lflick ).grid(row=1,column=0,columnspan=1, sticky="nwse")
	Button(x, text='⏸', command = chasis.noflick).grid(row=1,column=2,columnspan=1, sticky="nwse")
	Button(x, text='⮫', command = chasis.rflick ).grid(row=1,column=4,columnspan=1, sticky="nwse")
	Button(x, text='⛔', command = chasis.stop   ).grid(row=3,column=0,columnspan=5, sticky="nwse")

def build_center_frame(x):
	Img = Label(x, text='img', bg = 'red')
	Img.grid(row=0,column=0,sticky='nwse')
	x.rowconfigure(0, weight = 1)
	x.columnconfigure(0, weight = 1)
	# def place_widgets():
	# 	C0Scale.grid(row = 2, column = 1)
	# 	T0Scale.grid(row = 1, column = 1)
	# 	C1Scale.grid(row = 2, column = 3)
	# 	T1Scale.grid(row = 1, column = 3)
	# 	Img.grid(row = 1, column = 2, rowspan = 2)

	# def show_frame():
	#     _0, frame0 = cap0.read()
	#     frame0 = cv2.flip(frame0, 1)
	#     cv2image0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2RGBA)
	#     img0 = Image.fromarray(cv2image0)
	#     imgtk0 = ImageTk.PhotoImage(image=img0)
	#     Img.imgtk0 = imgtk0
	#     Img.configure(image=imgtk0)
	#     root.after(10, show_frame)
	pass

def build_right_frame(x): #⮘⮙⮚⮛
	Button(x, text='⮙', command = cam.up    ).grid(row=0,column=0,columnspan=3)
	Button(x, text='⮘', command = cam.left  ).grid(row=1,column=0,columnspan=1)
	Button(x, text='⭙', command = cam.center).grid(row=1,column=1,columnspan=1)
	Button(x, text='⮚', command = cam.right ).grid(row=1,column=2,columnspan=1)
	Button(x, text='⮛', command = cam.down  ).grid(row=2,column=0,columnspan=3)


def get_json_url_to_dict(cmd):
	try:
		return loads(urlopen(url_prefix + cmd).read().decode('UTF-8'))
	except Exception as e:
		return dict(
			ok = False,
			error = str(e),
		)

def post_json_url_to_dict(cmd, prm, vars = ()):
	try:
		post = (prm % vars).encode('UTF-8')
		return loads(urlopen(url_prefix + cmd, post).read().decode('UTF-8'))
	except Exception as e:
		return dict(
			ok = False,
			error = str(e),
		)

def update_speed_and_dir():
	if (req_acc_pos.get() > 0) and (0.6 < chasis.get_front_distance() < 1.3):
		res = chasis.stop(None)
	else:
		res = post_json_url_to_dict(
			cmd_move_set_acc_steer, 
			prm_move_set_acc_steer,
			(
				req_acc_pos.get(),
				0,
				0,
				req_str_pos.get()
			)
		)
	return res

def update_mismp():
	res = update_speed_and_dir()
	print(res)
	PNG.set(res['ok'])
	if PNG.get():
		_ = list(chasis.get_state(None))
		for scl in SPD, STP, AZM, U12V, I12V, I48V:
			scl.set(_.pop())
		
	t.after(50, update_mismp)

def exitprog(e):
	chasis.stop(e)
	exit()


t = Tk()
chasis = Chasis()
cam = CV()

req_str_pos = IntVar()
req_acc_pos = IntVar()

t.bind('w', chasis.more)
t.bind('a', chasis.left)
t.bind('s', chasis.stop)
t.bind('x', chasis.less)
t.bind('d', chasis.right)
t.bind('z', chasis.lbrake)
t.bind('c', chasis.rbrake)
t.bind('1', chasis.lflick)
t.bind('2', chasis.noflick)
t.bind('3', chasis.rflick)
t.bind('<Control_L>',chasis.stop)

t.bind('<Left>',cam.left)
t.bind('<Right>',cam.right)
t.bind('<Up>',cam.up)
t.bind('<Down>',cam.down)
t.bind('<Control_R>',cam.picture)

t.bind('<Escape>', exitprog)
t.after(500,update_mismp)

header,footer,pleft,pcenter,pright = build_frameset(t)
PNG, SPD, STP, AZM, U12V, I12V, I48V = build_header(header)
build_left_frame(pleft)
build_center_frame(pcenter)
build_right_frame(pright)
t.mainloop()

"""

--post-data="req_acc_pos=33&rgt_brk=1&lgt_brk=0" 'http://192.168.0.101:8000/engine/gooo' -q -O -
--post-data="req_acc_pos=33&rgt_brk=0&lgt_brk=1" 'http://192.168.0.101:8000/engine/gooo' -q -O -
--post-data="req_acc_pos=33&rgt_brk=1&lgt_brk=0" 'http://192.168.0.101:8000/engine/gooo' -q -O -
'http://192.168.0.101:8000/engine/stop' -q -O -
--post-data="req_acc_pos=31&rgt_brk=0&lgt_brk=0" 'http://192.168.0.101:8000/engine/gooo' -q -O -
'http://192.168.0.101:8000/engine/stop' -q -O -
--post-data="req_acc_pos=-31&rgt_brk=0&lgt_brk=0" 'http://192.168.0.101:8000/engine/gooo' -q -O -
'http://192.168.0.101:8000/engine/stop' -q -O -
--post-data="req_acc_pos=35&rgt_brk=0&lgt_brk=0" 'http://192.168.0.101:8000/engine/gooo' -q -O -
'http://192.168.0.101:8000/engine/stop' -q -O -
--post-data="req_acc_pos=-32&rgt_brk=0&lgt_brk=0" 'http://192.168.0.101:8000/engine/gooo' -q -O - ; sleep 1; wget'http://192.168.0.101:8000/engine/stop' -q -O -
--post-data="req_acc_pos=35&rgt_brk=0&lgt_brk=0" 'http://192.168.0.101:8000/engine/gooo' -q -O - ; sleep 1; wget 'http://192.168.0.101:8000/engine/stop' -q -O -
--post-data="req_acc_pos=-34&rgt_brk=0&lgt_brk=0" 'http://192.168.0.101:8000/engine/gooo' -q -O - ; sleep 1; wget 'http://192.168.0.101:8000/engine/stop' -q -O -
 5 ; wget --post-data="req_acc_pos=-34&rgt_brk=0&lgt_brk=0" 'http://192.168.0.101:8000/engine/gooo' -q -O - ; sleep 1; wget 'http://192.168.0.101:8000/engine/stop' -q -O -
 5 ; wget --post-data="req_acc_pos=31&rgt_brk=0&lgt_brk=0" 'http://192.168.0.101:8000/engine/gooo' -q -O - ; sleep 1; wget 'http://192.168.0.101:8000/engine/stop' -q -O -
 5 ; wget --post-data="req_acc_pos=31&rgt_brk=0&lgt_brk=0" 'http://192.168.0.101:8000/engine/gooo' -q -O - ; sleep 3; wget 'http://192.168.0.101:8000/engine/stop' -q -O -
--post-data="req_acc_pos=31&rgt_brk=0&lgt_brk=0" 'http://192.168.0.101:8000/engine/gooo' -q -O - ; sleep 3; wget 'http://192.168.0.101:8000/engine/stop' -q -O -
--post-data="req_acc_pos=31&rgt_brk=1&lgt_brk=0" 'http://192.168.0.101:8000/engine/gooo' -q -O - ; sleep 3; wget 'http://192.168.0.101:8000/engine/stop' -q -O -
'http://192.168.0.101:8000/power/measure' -q -O -
'http://192.168.0.101:8000/state' -q -O -
'http://192.168.0.101:8000/state/distances' -q -O -
--post-data="req_acc_pos=31&rgt_brk=0&lgt_brk=0&req_str_pos=0" 'http://192.168.0.101:8000/move/set_acc_steer' -q -O - 
--post-data="req_acc_pos=31&rgt_brk=0&lgt_brk=0&req_str_pos=10" 'http://192.168.0.101:8000/move/set_acc_steer' -q -O - 
--post-data="req_acc_pos=33&rgt_brk=0&lgt_brk=0&req_str_pos=10" 'http://192.168.0.101:8000/move/set_acc_steer' -q -O - 
'http://192.168.0.101:8000/engine/stop' -q -O -
--post-data="req_acc_pos=33&rgt_brk=0&lgt_brk=0&req_str_pos=10" 'http://192.168.0.101:8000/move/set_acc_steer' -q -O - 
'http://192.168.0.101:8000/engine/stop' -q -O -
--post-data="req_acc_pos=33&rgt_brk=0&lgt_brk=0&req_str_pos=10" 'http://192.168.0.101:8000/move/set_acc_steer' -q -O - 
--post-data="req_acc_pos=33&rgt_brk=0&lgt_brk=0&req_str_pos=0" 'http://192.168.0.101:8000/move/set_acc_steer' -q -O - 
--post-data="req_acc_pos=-33&rgt_brk=0&lgt_brk=0&req_str_pos=0" 'http://192.168.0.101:8000/move/set_acc_steer' -q -O - 
--post-data="req_acc_pos=33&rgt_brk=0&lgt_brk=0&req_str_pos=0" 'http://192.168.0.101:8000/move/set_acc_steer' -q -O - 
'http://192.168.0.101:8000/engine/stop' -q -O -
ry | grep wget | grep 101:8000 >> kru.py 
"""