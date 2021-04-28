#Create Setup.py file to make the module installable
from setuptools import setup, find_packages
from loko import LokoConfig, get_logger, models 
from loko.conf import CONFIG_FILENAME
import configparser
import os


setup(
	name = "loko",
	version = "0.1.3",
	author = "Mcflyhalf",
	author_email = "mcflyhalf@live.com",
	description = ("Store, send and receive money in different currencies"),
	keywords = "currency exchange forex",
	packages= find_packages(),
)

logger = get_logger("loko_setup")
config = configparser.ConfigParser()

config['DEFAULT'] = {}
default = config['DEFAULT']

default['install location'] = str(os.getcwd())	#Base install directory
default['sqlite production db'] = os.path.join(config['DEFAULT']['Install Location'], 'loko','models', 'loko_prod.db')
default['sqlite development db'] = os.path.join(config['DEFAULT']['Install Location'], 'loko','models', 'loko_dev.db')
default['sqlite test db'] = os.path.join(config['DEFAULT']['Install Location'], 'loko','tests', 'loko_test.db')
default['config_file'] = os.path.join(os.getcwd(), CONFIG_FILENAME)

#Create config file
with open(CONFIG_FILENAME, 'w') as configfile:
	config.write(configfile)


prod_engine = models.production_engine
LokoConfig(prod_engine, logger).newconfig(prod_engine)

dev_engine = models.development_engine
LokoConfig(dev_engine, logger).newconfig(dev_engine)


