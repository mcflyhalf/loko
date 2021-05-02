import os
import logging
from logging.handlers import RotatingFileHandler
from loko.conf import get_configs


def get_logger(loggerName):
	log = logging.getLogger(loggerName)
	# File handler which logs even debug messages
	# To atttempt compression of old log files, try https://docs.python.org/3/howto/logging-cookbook.html#using-a-rotator-and-namer-to-customize-log-rotation-processing
	config = get_configs()
	log_location = os.path.join(config['install location'],'log','loko.log')
	if not os.path.exists(log_location):
		os.makedirs(log_location[:len('loko.log')*-1])
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
