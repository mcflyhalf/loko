import os
import logging
from logging.handlers import RotatingFileHandler
from loko.conf import get_configs
from loko import models
from loko.models.models import Base, Wallets, SupportedCurrencies

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

#TODO: Move to conf.py
class LokoConfig:
	def __init__(self, engine, logger):
		self.logger = logger
		# self.newconfig(engine)

	def create_tables(self, engine):
		print("Getting the tables")
		tables = models.get_tables_metadata()
		for table in tables:
			print("Creating table *{}*".format(table.name))
			self.logger.info("Creating table *{}*".format(table.name))
			#create_all will not recreate existing tables
			Base.metadata.create_all(engine, tables=[table], checkfirst=True)
			self.logger.info("Table {} created successfully".format(table.name))

	def drop_tables(self, engine):
		tables = models.get_tables_metadata()
		tables.reverse()
		self.logger.warning("Deleting all tables")
		#Do dangerous stuff here and log as each table is deleted
		for table in tables:
			self.logger.warning("Deleting table *{}*".format(table.name))
			#TODO: Move use of Base away from here to somewhere in loko.models
			Base.metadata.drop_all(engine, tables=[table])
			self.logger.info("Table *{}* deleted successfully".format(table.name))

		self.logger.info("Tables deleted successfully!")

	def newconfig(self, engine, drop_tables=False):	#For a new install
		'''
		if drop_tables, drop all tables and create afresh, otherwise
		#only create new tables
		'''
		if drop_tables:
			self.drop_tables(engine)
		self.create_tables(engine)

def get_wallet_from_user(session, user):
	wallet = (session.query(Wallets)
					.filter(Wallets.ownerid==user.id)
					.one())
	return wallet

def get_wallet_attrs_from_user(session, user):
	wlt = get_wallet_from_user(session, user)
	wlt_cur_enum = SupportedCurrencies[wlt.currency_alpha_code]
	balance_format_string = '{:,.'+str(wlt_cur_enum.value['minor unit'])+'f}'
	wallet = {}
	wallet['currency'] = wlt_cur_enum
	wallet['currency symbol'] = wlt_cur_enum.value['symbol']
	wallet['currency_alpha_code'] = wlt_cur_enum.name
	wallet['actual balance'] = wlt.balance
	#TODO: Should truncate, not round off
	wallet['display balance'] = balance_format_string.format(wlt.balance) 
	wallet['id'] = wlt.id

	return wallet
