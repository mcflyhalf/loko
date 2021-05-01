# Business logic for creation of transactions
from datetime import datetime, timezone
from loko.utils import get_logger
from loko.models.models import Wallets, Users, Currencies, Transactions, SupportedCurrencies
from loko.models import get_db_session	# Not required, todelete

logger = get_logger("loko_transactor")
TRANSACTION_COMMISSION = 0.01
MAX_COMISSION = 0.08
LOKO_WALLET_ID = 0
COMISSION_NARRATIVE = "Charges for transaction "

#TODO: Add detailed logging for this class
#It is business critical
class TransactionCreator:
	'''
	Class that handles logic of transferring money from 1 wallet to another
	:param session: the db connection session
	:param origin_wallet_id: wallet_id of the source of funds
	:param origin_user_id: user_id of the transaction initiator. Must be an owner of the wallet

	:raises AuthenticationError: if origin_user_id is not wallet.ownerid (TODO: Currently raises the wrong exception)
	'''
	def __init__(self, session, origin_wallet_id, origin_user_id):
		self.session = session
		self.origin_wallet_id = origin_wallet_id
		self.origin_user_id = origin_user_id
		self.origin_wallet = (session.query(Wallets)
							.filter(Wallets.id==origin_wallet_id)
							.one())
		self.origin_user = (session.query(Users)
							.filter(Users.id==origin_user_id)
							.one())

	def send(self,amount, currency_enum, destination_wallet_id, narrative):
		'''
		currency here is the enum. Later, it will be an object from the db
		This is done to avoid the possibility of tampering with exchange rate
		'''
		#Check source user has permission to access the wallet
		try:
			assert amount > 0
		except AssertionError:
			raise ValueError("Amount sent must be greater than 0.\
							Requested amount was {}".format(amount))
		try:
			assert self.origin_wallet.ownerid == self.origin_user.id
		except AssertionError:
			raise PermissionError("User {} has no access to wallet id>{}<"
								.format(self.origin_user.username, self.origin_wallet.id))

		#Check that the currency specified is either the source or destination wallet's currency
		destination_wallet = (self.session.query(Wallets)
									.filter(Wallets.id==destination_wallet_id)
									.one())
		try:
			assert currency_enum.name == self.origin_wallet.currency_alpha_code or \
					currency_enum.name == destination_wallet.currency_alpha_code
		except AssertionError:
			raise ValueError("Currency {} given does not match source or destination wallet currencies.\
				currency, should be {} or {}".format(currency_enum.name, self.origin_wallet.currency_alpha_code, destination_wallet.currency_alpha_code))

		#Convert amount into source wallet currrency
		request_currency = currency_enum
		origin_wallet_currency = self.origin_wallet.currency_alpha_code
			#Convert to enum type
		origin_wallet_currency = SupportedCurrencies[origin_wallet_currency]
		currency_converter = CurrencyConverter(self.session)
		conversion = currency_converter.convert(amount,request_currency,origin_wallet_currency)
		#Slightly confusing below. 
		#Destination is the destination of the conversion, not destination of the transaction
		#It is in fact the origin/source of the transaction
		origin_curr_amt = conversion['destination amount']

		#Check source wallet has enough funds to cover cost of transaction and comission
		comission = self.calculate_comission(origin_curr_amt)
		try:
			assert self.origin_wallet.balance > origin_curr_amt + comission
		except AssertionError:
			raise ValueError("Wallet has insufficient funds to cover transaction of {} and comission of {}\
								Wallet balance is {} but needs to be more than{}".\
						format(origin_curr_amt, comission, self.origin_wallet.balance, origin_curr_amt + comission))

		#Transact (2 transactions: the requested one and commision)
		try:
			origin_curr_obj = (self.session.query(Currencies)
								.filter(Currencies.alphabetic_code==origin_wallet_currency.name)
								.one())
				#Requested transaction
			req_mf=self._move_funds(origin_curr_amt, origin_curr_obj, self.origin_wallet.id, destination_wallet.id)
				#Comission
			com_mf=self._move_funds(comission, origin_curr_obj, self.origin_wallet.id, LOKO_WALLET_ID)
			req_tx=self._create_transaction(datetime.now(timezone.utc),self.origin_wallet.id,destination_wallet_id,self.origin_user.id,origin_curr_amt,origin_curr_obj.alphabetic_code,conversion['exchange rate'],narrative,self.session)
			com_nrtv = COMISSION_NARRATIVE+str(req_tx.id)
			com_tx=self._create_transaction(datetime.now(timezone.utc),self.origin_wallet.id,LOKO_WALLET_ID,self.origin_user.id,comission,origin_curr_obj.alphabetic_code,conversion['exchange rate'],com_nrtv,self.session)
		except Exception as e:
			self.session.rollback()
			raise e #ValueError("General transaction error. Transaction aborted")

		return req_mf

		

	def calculate_comission(self,amount, commision=TRANSACTION_COMMISSION):
		assert TRANSACTION_COMMISSION <= MAX_COMISSION
		assert TRANSACTION_COMMISSION > 0
		assert MAX_COMISSION < 1

		return amount * TRANSACTION_COMMISSION

	def _create_transaction(self,date_time,source_wallet_id,destination_wallet_id,origin_user_id,amount,origin_currency_code,exchange_rate,narrative,session):
		'''
		Persists a transaction record to be stored in the db.
		These records are used to create statements
		:param date: transaction date. Datetime object
		:param origin_wallet_id: Origin Wallet ID
		:param destination_wallet_id: Destination wallet ID
		:param amount: Amount transferred expressed in origin currency
		:param currency: Currency of amount transferred. MUST be origin currency (not enforced)
		:param exchange_rate: Exchange rate used (=1 if origin and destination wallet have same currency)
		:param narrative: Transaction's narrative, limited to 40 characters

		:returns Transaction: The created transaction object
		'''
		transaction = Transactions(
					date_time=date_time,
					origin=source_wallet_id,
					destination=destination_wallet_id,
					originator=origin_user_id,
					amount=amount,
					currency=origin_currency_code,
					exchange_rate=exchange_rate,
					narrative=str(narrative)[:40]
					)
		session.add(transaction)
		session.commit()

		return transaction



	def _move_funds(self,amount, currency_obj, source_wallet_id, destination_wallet_id):
		'''
		Requires funds to be in the source wallet currency
		currency_obj is an ORM instance. Contains exchange rate
		currency_obj MUST be in the same currency as the source wallet
		'''
		sess = self.session
		currency = currency_obj
		source_wallet= sess.query(Wallets).filter(Wallets.id==source_wallet_id).one()
		destination_wallet= sess.query(Wallets).filter(Wallets.id==destination_wallet_id).one()

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
	def __init__(self,session):
		self.session = session

	def convert(self,amount, source_currency_enum, destination_currency_enum):
		exchange_rate = self.get_exchange_rate(source_currency_enum, destination_currency_enum)
		result = {}
		result['source currency'] = source_currency_enum.name
		result['destination_currency'] = destination_currency_enum.name
		result['source amount'] = amount
		result['destination amount'] = amount*exchange_rate
		result['exchange rate'] = exchange_rate

		return result

	def get_exchange_rate(self,source_currency_enum, destination_currency_enum):
		#same currency, no need to do maths
		if source_currency_enum == destination_currency_enum:
			return 1.0
		s_alphacode = source_currency_enum.name
		d_alphacode = destination_currency_enum.name
		source_currency = (self.session.query(Currencies)
						.filter(Currencies.alphabetic_code==s_alphacode)
						.one())
		destination_currency = (self.session.query(Currencies)
						.filter(Currencies.alphabetic_code==d_alphacode)
						.one())

		#Given exchange rates of base to source and dest currency as:
		# r_bs and r_bd
		# Then the exchange rate of source to destination, r_sd, is given by:
		# r_sd = r_bd/r_bs
		r_bs = source_currency.xchange_rate
		r_bd = destination_currency.xchange_rate

		r_sd = r_bd/r_bs

		return r_sd


#Using this as a quick and dirty manual test
#Will delete once proper automated tests are created
if __name__ == '__main__':
	session = get_db_session()
	origin_wallet_id = 1	#GBP
	origin_user_id = origin_wallet_id
	destination_wallet_id = 6	#JPY
	destination_user_id = destination_wallet_id
	amount_to_send = 250
	to_send_currency_enum = SupportedCurrencies['GBP'] #Try other currencies
	source_currency_enum = to_send_currency_enum
	to_receive_currency_enum = SupportedCurrencies['JPY']
	destination_currency_enum = to_receive_currency_enum


	narrative = "Test payments"


	#Test currency converter
	# cc = CurrencyConverter(session)
	# conv = cc.convert(amount_to_send, to_send_currency_enum, to_receive_currency_enum)
	# print(conv)

	#Test end-2-end transaction
	tc = TransactionCreator(session, origin_wallet_id, origin_user_id)
	tc.send(amount_to_send, to_send_currency_enum, destination_wallet_id, narrative)




