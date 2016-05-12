from urllib.request import urlopen
from json import loads, dumps

class CV():
	NAME             = 'CV'

	cmd_state 		 = '/state'
	cmd_describe 	 = '/describe'
	cmd_list_objects = '/list_objects'
	cmd_left 		 = '/left'
	cmd_right 		 = '/right'
	cmd_wide 		 = '/wide'
	cmd_recognize 	 = '/recognize'
	prm_recognize 	 = "a[]='%i'&a[]='%i'&b[]='%i'&b[]='%i'"
	cmd_find 		 = '/find'
	cmd_scan 		 = '/scan'
	prm_scan		 = "a_min=%i&a_max=%i"
	cmd_rotate 		 = '/rotate'
	prm_rotate 		 = 'a=%i&b=%i&returnimage=0'
	cmd_range 		 = '/range'
	cmd_cloud 		 = '/cloud'
	img_wide		 = 'http://192.168.0.115/jpg/1/image.jpg?resolution=640x480'

	def __get_img_url_to_dict(self, imgurl):
		try:
			return dict(
				img = urlopen(self.url_prefix + imgurl).read(),
				ok = True,
			)
		except Exception as e:
			return dict(
				ok = False,
				error = "%s / %s / %s " % (str(e), '__get_img_url_to_dict', imgurl),
			)


	def __get_json_url_to_dict(self, cmd):
		try:
			return loads(urlopen(self.url_prefix + cmd).read().decode('UTF-8'))
		except Exception as e:
			return dict(
				ok = False,
				error = "%s / %s / %s " % (str(e), '__get_json_url_to_dict', cmd),
			)

	def __post_json_url_to_dict(self, cmd, prm, vars = ()):
		try:
			post = (prm % vars).encode('UTF-8')
			return loads(urlopen(self.url_prefix + cmd, post).read().decode('UTF-8'))
		except Exception as e:
			return dict(
				ok = False,
				error = "%s / %s / %s / %s" % (str(e), '__post_json_url_to_dict', cmd, prm),
			)

	def set_current_cam(self, current_cam = 'left'):
		if current_cam in self.cam_list.keys():
			self.current_cam = current_cam
		return self.get_state()

	def get_state(self):
		x = self.__get_json_url_to_dict(self.cmd_state)
		x.update({'current_cam': self.current_cam})
		if x['state'] != 'NORMAL_OP': 
			raise Exception('CV error ' + x['state'])
		else: 
			x.update({'ok':True})
		return x

	def get_description(self):
		return self.__get_json_url_to_dict(self.cmd_describe)

	def get_object_list(self):
		return self.__get_json_url_to_dict(self.cmd_list_objects)

	def picture(self):
		if self.current_cam == 'left':
			return self.get_left()
		elif self.current_cam == 'right':
			return self.get_right()
		elif self.current_cam == 'wide':
			return self.get_wide()
		else:
			return self.get_left()

	def get_left(self):
		return self.__get_img_url_to_dict(self.__get_json_url_to_dict(self.cmd_left))

	def get_right(self):
		return self.__get_img_url_to_dict(self.__get_json_url_to_dict(self.cmd_right))

	def get_wide(self):
		try:
			return dict(
				img = urlopen(self.img_wide).read(),
				ok = True,
			)
		except Exception as e:
			return dict(
				ok = False,
				error = str(e),
			)

	def do_recognize(self):
		return self.__post_json_url_to_dict(self.cmd_recognize, self.prm_recognize, (1,-1,1,-1))

	def do_find(self):
		x = {}
		return x

	def do_scan(self, a_min, a_max):
		x = self.__post_json_url_to_dict(self.cmd_scan, self.prm_scan, (a_min, a_max))
		return x

	def do_rotate(self, a, b):
		_ = {}
		y = self.__post_json_url_to_dict(self.cmd_rotate, self.prm_rotate, (a, b))
		print(y)
		_.update()
		_.update(self.__get_json_url_to_dict(self.cmd_state))
		return _

	def do_range(self):
		x = {}
		return x

	def do_cloud(self):
		x = {}
		return x


	current_cam      = 'left'
	cam_list		 = {
		'left': get_left,
		'right': get_right,
		'wide': get_wide
	}
	
	def __init__(self, url='http://192.168.0.198:8000'):
		self.url_prefix = url
		self.state = {}
		self.state.update({'current_cam': self.current_cam})
		for m in [self.get_state, self.get_description]:
			self.state.update(m())

def NoneFunc():
	post = json.dumps(cmd).encode('UTF-8')
	response = urlopen(CAMERA_URL + 'rotate', post)
	#print(response.read())
	self.load_str(response.read().decode('UTF-8'))

if __name__ == "__main__":
	cv = CV()
	print(cv.state)
	print(cv.get_object_list())
