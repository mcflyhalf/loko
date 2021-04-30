import os
import configparser

CONFIG_FILENAME = 'loko_config.cfg'

def get_configs(profile = 'DEFAULT'):
	
	curdir = os.path.dirname(__file__)	#The Path to this conf script.
	curdir = os.path.abspath(curdir)
	config = configparser.ConfigParser()
	config.read(os.path.join(curdir,'..',CONFIG_FILENAME))
	
	return config[profile]
