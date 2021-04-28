#Create Setup.py file to make the module installable
from setuptools import setup, find_packages
from loko import get_logger, CONFIG_FILENAME#, production_engine, test_engine, 
import configparser
import os
from loko import models
from loko.models.models import Base

setup(
	name = "loko",
	version = "0.1.2",
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

class LokoConfig:
	def __init__(self, engine):
		self.newconfig(engine)

	def create_tables(self, engine):
		print("Getting the tables")
		tables = models.get_tables_metadata()
		for table in tables:
			print("Creating table *{}*".format(table.name))
			logger.info("Creating table *{}*".format(table.name))
			#create_all will not recreate existing tables
			Base.metadata.create_all(engine, tables=[table], checkfirst=True)
			logger.info("Table {} created successfully".format(table.name))

	def drop_tables(self, engine):
		tables = models.get_tables_metadata()
		tables.reverse()
		logger.warn("Deleting all tables")
		#Do dangerous stuff here and log as each table is deleted
		for table in tables:
			logger.warn("Deleting table *{}*".format(table.name))
			#TODO: Move use of Base away from here to somewhere in loko.models
			Base.metadata.drop_all(engine, tables=[table])
			logger.info("Table *{}* deleted successfully".format(table.name))

		logger.info("Tables deleted successfully!")

	def newconfig(self, engine):	#For a new install
		# self.drop_tables(engine)
		self.create_tables(engine)

prod_engine = models.production_engine
LokoConfig(prod_engine)

dev_engine = models.development_engine
LokoConfig(dev_engine)


