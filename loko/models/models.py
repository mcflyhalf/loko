from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean
from loko.models import Base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum, unique, auto

currency_code = String(3)
wallet_id = Integer
user_id = Integer
wallet_balance = Float

#TODO: Discuss with other devs. Currently trying to avoid using an api
#Obtained info from https://en.wikipedia.org/wiki/ISO_4217
currency_info = {
	'EUR':{'common name': 'Euro','minor unit':2},
	'USD':{'common name': 'United States dollar','minor unit':2},
	'GBP':{'common name': 'Pound sterling','minor unit':2},
	'JPY':{'common name': 'Japanese yen','minor unit':0},
	'CHF':{'common name': 'Swiss franc','minor unit':2},
	'CNY':{'common name': 'Chinese yuan','minor unit':2},
	'AUD':{'common name': 'Australian dollar','minor unit':2},
	'CAD':{'common name': 'Canadian dollar','minor unit':2},
	'INR':{'common name': 'Indian rupee','minor unit':2},
	'ZAR':{'common name': 'South African rand','minor unit':2}
}

#TODO: Consider moving supported currencies away from code
#TODO: Represent Base currency as an alias
#So configuration doesnt require changing code
#Because of the way this is implemented, supporting a currency requires
#that it exists in loko.models.models.currency_info
@unique
class SupportedCurrencies(Enum):
	def _generate_next_value_(name, start, count, last_values):
		'''
		overidden so that auto generates value of the form:
		{'common name': 'United States dollar','minor unit':2}
		depends on loko.models.models.currency_info
		'''
		vals = {}
		vals['common name'] = currency_info[name]['common name']
		vals['minor unit'] = currency_info[name]['minor unit']
		return vals

	EUR = auto()
	USD = auto()
	GBP = auto()
	JPY = auto()
	CHF = auto()
	CNY = auto()
	AUD = auto()
	CAD = auto()
	INR = auto()
	ZAR = auto()

class Currencies(Base):
	__tablename__ = "currencies"

	alphabetic_code = Column(currency_code, primary_key=True)
	numeric_code = Column(Integer, unique=True, nullable=True)
	minor_unit = Column(Integer, nullable=False)
	xchange_rate = Column(Float, nullable=False)
	name = Column(String, nullable=True)

class Wallets(Base):
	__tablename__ = "wallets"

	id = Column(wallet_id, primary_key=True)
	ownerid = Column(user_id, ForeignKey("users.id"), nullable=False)
	currency_alpha_code = Column(currency_code, ForeignKey("currencies.alphabetic_code"), nullable=False)
	balance = Column(wallet_balance, nullable=False)

class Transactions(Base):
	'''
	A transaction is debited from origin Wallet and debited to destination wallet
	A transaction may only be requested in the currency of origin or destination wallet
	Note that a user may change the currency of a wallet hence the current currency is
	not necessarily what was current at the time of transaction
	:field id: Transaction ID
	:field date: ISO8601 datetime representation of transaction datetime
	:field origin: Origin Wallet ID
	:field destination: Destination wallet ID
	:field amount: Amount transferred
	:field currency: Currency of amount transferred
	:field exchange_rate: Exchange rate used (=1 if origin and destination wallet have same currency)
	'''
	__tablename__ = "transactions"

	id = Column(Integer, primary_key=True)
	date = Column(DateTime, nullable=False)
	origin = Column(wallet_id, ForeignKey("wallets.id"), nullable=False)
	destination = Column(wallet_id, ForeignKey("wallets.id"), nullable=False)
	originator = Column(user_id, ForeignKey("users.id"), nullable=False)
	amount = Column(wallet_balance, nullable=False)
	currency = Column(currency_code, ForeignKey("currencies.alphabetic_code"), nullable=False)
	exchange_rate = Column(Float, nullable=False)


class Users(Base):
	__tablename__ = "users"

	id = Column(user_id, primary_key=True)
	username = Column(String(20),nullable=False,unique=True)	#Always Lowercase
	name = Column(String,nullable=False)
	email = Column(String(50),nullable=False)
	authenticated = Column(Boolean, nullable=False)
	active = Column(Boolean, nullable=False)
	password_hash = Column(String, nullable=False)

	annonymous = False

# See comment at https://realpython.com/using-flask-login-for-user-management-with-flask/ about login and logout
	def is_authenticated(self):
		return self.authenticated

	def is_active(self):
		return self.active

	def is_annonymous(self):
		return self.annonymous

	def check_password(self,password):
		self.authenticated = check_password_hash(self.password_hash, str(password))
		return self.is_authenticated()

	def get_id(self):
		return str(self.id)

	def set_password(self,raw_password):
		self.password_hash = generate_password_hash(str(raw_password))
