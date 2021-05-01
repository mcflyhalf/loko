from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from loko import models
from loko.biz.xchange import get_xchange_data, save_xchange_data
from loko.models import Base
from loko.models.models import Wallets, SupportedCurrencies, Users
from loko.app import app

def get_app():
	return app


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

	def newconfig(self, engine, xchange_data_pkl, drop_tables=False):	#For a new install
		'''
		if drop_tables, drop all tables and create afresh, otherwise
		only create new tables
		Also ensure that the Loko Admin user exists to receive comission
		'''
		if drop_tables:
			self.drop_tables(engine)
		self.create_tables(engine)

		Session = sessionmaker(bind=engine)
		session = Session()

		try:
			q = session.query(Users).filter(Users.id == 0)
			existing_admin = q.one()
		except NoResultFound:
			#Admin does not exist yet
			admin = {}
			admin['id'] = 0
			admin['username'] = 'lokoadmin'
			admin['name'] = 'Loko Admin'
			admin['email'] = 'admin@lo.ko'
			admin['default_currency_alpha_code'] = 'EUR'	#TODO: Unhardcode
			admin['authenticated'] = False
			admin['active'] = True
			admin['password_hash'] = 'CantLogin'
			admin_user = Users(**admin)
			session.add(admin_user)
		else:
			#currency already exists.  Make sure the values are what we want
			assert isinstance(existing_admin, Users)
		session.flush()

		try:
			q = session.query(Wallets).filter(Wallets.ownerid == 0)
			existing_admin_wallet = q.one()
		except NoResultFound:
			#Admin does not exist yet
			admin_wlt = {}
			admin_wlt['id'] = 0
			admin_wlt['ownerid'] = admin_user.id
			admin_wlt['currency_alpha_code'] = admin_user.default_currency_alpha_code
			admin_wlt['balance'] = 0
			admin_wallet = Wallets(**admin_wlt)
			session.add(admin_wallet)
		else:
			#currency already exists.  Make sure the values are what we want
			assert isinstance(existing_admin_wallet, Wallets)		
		session.flush()

		xchange_data = get_xchange_data(xchange_data_pkl)
		save_xchange_data(xchange_data, session=session, save_to_db=True)

		session.commit()
