import yaml
__config = None #Catches the confing


def config():
	global __config
	if not __config:
		with open('config.yaml', mode='r') as f:
			__config = yaml.safe_load(f)
	return __config #we return the object config with all the variables in config.yaml