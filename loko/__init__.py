import os
import logging
from logging.handlers import RotatingFileHandler
import configparser


CONFIG_FILENAME = 'loko_config.cfg'

def get_configs(profile = 'DEFAULT'):
	
	curdir = os.path.dirname(__file__)	#The Path to this __init__ file.
	curdir = os.path.abspath(curdir)
	config = configparser.ConfigParser()
	config.read(os.path.join(curdir,'..',CONFIG_FILENAME))
	
	return config[profile]


def get_logger(loggerName):
	log = logging.getLogger(loggerName)
	# File handler which logs even debug messages
	# To atttempt compression of old log files, try https://docs.python.org/3/howto/logging-cookbook.html#using-a-rotator-and-namer-to-customize-log-rotation-processing
	config = get_configs()
	log_location = os.path.join(config['install location'],'log','loko.log')
	fh = RotatingFileHandler(log_location, mode='a', maxBytes=1*1024*1024,backupCount=10, encoding=None, delay=0)
	fh.setLevel(logging.DEBUG)
	# Console handler that logs warnings or higher
	ch = logging.StreamHandler()
	ch.setLevel(logging.WARNING)
	# create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)
	# add the handlers to the logger
	log.addHandler(fh)
	log.addHandler(ch)
	log.setLevel(logging.DEBUG)
	return log