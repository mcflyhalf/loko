from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean
from loko.models import Base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

currency_code = String(3)
wallet_id = String
user_id = Integer
wallet_balance = Float

class Currencies(Base):
	__tablename__ = "currencies"

	alphabetic_code = Column(currency_code, primary_key=True)
	numeric_code = Column(Integer, unique=True, nullable=False)
	minor_unit = Column(Integer, nullable=False)
	name = Column(String)

class Wallets(Base):
	__tablename__ = "wallets"

	id = Column(wallet_id, primary_key=True)
	currency = Column(currency_code, ForeignKey("currencies.alphabetic_code"), nullable=False)
	balance = Column(wallet_balance, nullable=False)

class Transactions(Base):
	__tablename__ = "transactions"

	id = Column(Integer, primary_key=True)
	date = Column(DateTime, nullable=False)
	origin = Column(wallet_id, ForeignKey("wallets.id"), nullable=False)
	destination = Column(wallet_id, ForeignKey("wallets.id"), nullable=False)
	originator = Column(user_id, ForeignKey("users.id"), nullable=False)
	amount = Column(wallet_balance, nullable=False)
	currency = Column(currency_code, ForeignKey("currencies.alphabetic_code"), nullable=False)



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
