import subprocess

def get_top_responce():
	top_response = subprocess.Popen(['top', '-b', '-n', '1'], stdout=subprocess.PIPE).stdout.read()
	return '\n'.join(top_response.decode("utf-8").split('\n')[0:5])

