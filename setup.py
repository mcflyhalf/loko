#Create Setup.py file to make the module installable
from setuptools import setup, find_packages
from loko import LokoConfig, get_logger, models 
from loko.conf import CONFIG_FILENAME
from loko.biz.xchange import XCHANGE_FILENAME_BASE
from loko.tests.populate import populate_db
import configparser
import os


setup(
	name = "loko",
	version = "0.2.0",
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
default['exchange rate base filename'] = XCHANGE_FILENAME_BASE
default['exchange rate file location'] = os.path.join(config['DEFAULT']['Install Location'], 'loko','biz', 'xchange_data')
default['exchange rate test response'] = os.path.join(config['DEFAULT']['Install Location'], 'loko','tests', 'test_xchange_resp.pkl')
#Create config file
with open(CONFIG_FILENAME, 'w') as configfile:
	config.write(configfile)


prod_engine = models.production_engine
LokoConfig(prod_engine, logger).newconfig(prod_engine,drop_tables=False)

dev_engine = models.development_engine
LokoConfig(dev_engine, logger).newconfig(dev_engine,drop_tables=True)

#Populate the dev db for dev testing
#For some reason `pip install -e .` seems to run this entire file twice over
logger.info("Preparing to populate dev database")
xchange_resp_file = default['exchange rate test response']
dev_session = models.get_db_session(env="development")
logger.info("Starting to populate dev database")
populate_db(dev_session, xchange_resp_file)
logger.info("Finished populating dev database")