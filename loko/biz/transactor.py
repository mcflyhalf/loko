# Business logic for creation of transactions
from loko.models.models import Wallets, Users, Currencies

TRANSACTION_COMMISSION = 0.01

#TODO: Add detailed logging for this class
#It is business critical
class TransactionCreator:
	'''
	Class that handles logic of transferring money from 1 wallet to another
	:param session: the db connection session
	:param origin_wallet_id: wallet_id of the source of funds
	:param origin_user_id: user_id of the transaction initiator. Must be an owner of the wallet

	:raises AuthenticationError: if origin_user_id is not wallet.ownerid 
	'''
	def __init__(session, origin_wallet_id, origin_user_id):
		self.session = session
		self.origin_wallet = origin_wallet
		self.origin_user = origin_user

	def send(amount, currency_enum, to=destination_wallet):
		'''
		currency here is the enum. Later, it will be an object from the db
		This is done to avoid the possibility of tampering with exchange rate
		'''
		#Check source user has permission to access the wallet

		#Check that the currency specified is either the source or destination wallet's currency

		#Convert amount into source wallet currrency

		#Check source wallet has enough funds to cover cost of transaction and comission

		#Transact (2 transactions: the requested one and commision)

		pass



	def create_transaction_with_commision():
		pass

	def calculate_comission():
		pass

	def _create_transaction():
		pass

	def _move_funds(amount, currency_obj, source_wallet_id, destination_wallet_id):
		'''
		Requires funds to be in the source wallet currency
		currency_obj is an ORM instance. Contains exchange rate
		currency_obj MUST be in the same currency as the source wallet
		'''
		sess = self.session
		currency = currency_obj
		source_wallet= sess.query(Wallets).filter_by(sth=sth).one()
		destination_wallet= sess.query(Wallets).filter_by(sth=sth).one()

		assert source_wallet.currency_alpha_code == currency.alphabetic_code

		# get  wallet currency
		d_currency = destination_wallet.currency_alpha_code
		s_currency = source_wallet.currency_alpha_code
			#Convert to enum type
		d_currency = SupportedCurrencies[d_currency]
		s_currency = SupportedCurrencies[s_currency]

		# convert amount to dest wallet currency
		#The following may be different because of different wallet currencies
		currency_converter = CurrencyConverter(sess)
		debit_amount = amount
		conversion = currency_converter.convert(debit_amount,s_currency,d_currency)
		credit_amount = conversion['destination amount']

		try:
			source_wallet.balance -= debit_amount
			destination_wallet.balance += credit_amount
		except:
			sess.rollback()
			raise ValueError("Unable to move funds >>{}<<from wallet with id {}\
			 to wallet with id {}".format(debit_amount, source_wallet.id, destination_wallet.id))

		result = conversion
		result['source balance'] = source_wallet.balance
		result['destination balance'] = destination_wallet.balance
		return result

		# debit source and credit destination


class CurrencyConverter:
	def __init__(session):
		self.session = session

	def convert(amount, source_currency_enum, destination_currency_enum):
		exchange_rate = self.get_exchange_rate(source_currency_enum, destination_currency_enum)
		result = {}
		result['source currency'] = source_currency_enum.name
		result['destination_currency'] = destination_currency_enum.name
		result['source amount'] = amount
		result['destination amount'] = amount*exchange_rate
		result['exchange rate'] = exchange_rate

		return result

	def get_exchange_rate(source_currency_enum, destination_currency_enum):
		#same currency, no need to do maths
		if source_currency_enum == destination_currency_enum:
			return 1.0
		s_alphacode = source_currency_enum.name
		d_alphacode = destination_currency_enum.name
		source_currency = session.\
						query(Currencies).
						filter_by(Currencies.alphabetic_code=s_alphacode).
						one()
		destination_currency = session.\
						query(Currencies).
						filter_by(Currencies.alphabetic_code=d_alphacode).
						one()

		#Given exchange rates of source and dest to base currency as:
		# r_sb and r_db
		# Then the exchange rate of source to destination, r_sd, is given by:
		# r_sd = r_db/r_sb
		r_sb = source_currency.xchange_rate
		r_db = destination_currency.xchange_rate

		r_sb = r_db/r_sb

		return r_db


