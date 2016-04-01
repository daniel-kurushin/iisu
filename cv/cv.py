from urllib.request import urlopen
from json import loads, dumps

class CV():
	name             = 'CV'
	
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
	prm_rotate 		 = 'a=%i&b=%i'
	cmd_range 		 = '/range'
	cmd_cloud 		 = '/cloud'

	def __get_json_url_to_dict(self, cmd):
		try:
			return loads(urlopen(self.url_prefix + cmd).read().decode('UTF-8'))
		except Exception as e:
			return dict(
				ok = False,
				error = str(e),
			)

	def __post_json_url_to_dict(self, cmd, prm, vars = ()):
		try:
			post = (prm % vars).encode('UTF-8')
			return loads(urlopen(self.url_prefix + cmd, post).read().decode('UTF-8'))
		except Exception as e:
			return dict(
				ok = False,
				error = str(e),
			)

	def get_state(self):
		x = self.__get_json_url_to_dict(self.cmd_state)
		if x['state'] != 'NORMAL_OP': 
			raise Exception('CV error ' + x['state'])
		else: 
			x.update({'ok':True})
		return x

	def get_description(self):
		return self.__get_json_url_to_dict(self.cmd_describe)

	def get_object_list(self):
		return self.__get_json_url_to_dict(self.cmd_list_objects)

	def get_left(self):
		x = {}
		return x

	def get_right(self):
		x = {}
		return x

	def get_wide(self):
		x = {}
		return x

	def do_recognize(self):
		return self.__post_json_url_to_dict(cv.cmd_recognize, cv.prm_recognize, (1,-1,1,-1))

	def do_find(self):
		x = {}
		return x

	def do_scan(self, a_min, a_max):
		x = self.__post_json_url_to_dict(cv.cmd_scan, cv.prm_scan, (a_min, a_max))
		return x

	def do_rotate(self, a, b):
		x = self.__post_json_url_to_dict(cv.cmd_rotate, cv.prm_rotate, (a, b))
		return x

	def do_range(self):
		x = {}
		return x

	def do_cloud(self):
		x = {}
		return x


	def __init__(self, url='http://192.168.0.198:8000'):
		self.url_prefix = url
		self.state = {}
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
