# Business logic for creation of entities
# Transaction entities are not created here though
# They are created in transactor.py (subject to change)
from loko.models import models
from loko import get_logger

logger = get_logger('loko_creator')
#Changing this doesnt affect existing records
DEFAULT_CURRENCY_ALPHA_CODE = 'GBP'


class UserCreator:
	'''
	Contains logic for creating a new user
	Will Implement things such as creating a wallet for the user
	Expected kwargs:
	username - user's username
	password - user's raw password
	name - user's name
	email - user's email address
	authenticated - Bool, whether user is authed
	active - Bool, whether user is active

	currency='GBP' - (optional) ISO4217 currency alphabetic code.
	'''
	def __init__(self, session, **kwargs):
		'''
		Expected kwargs:
		username - user's username
		password - user's raw password
		name - user's name
		email - user's email address
		authenticated - Bool, whether user is authed
		active - Bool, whether user is active

		currency='GBP' - (optional) ISO4217 currency alphabetic code.
		'''
		self.kwargs = kwargs
		self.session=session

	def create_user(self):
		'''
		Create a user and associated wallet
		Default wallet currency is set at top of this file
		'''
		user = self._create_user_only()
		user_currency = DEFAULT_CURRENCY_ALPHA_CODE
		# user_currency = self.kwargs.get('currency')
		if user_currency is None:
			user_currency = DEFAULT_CURRENCY_ALPHA_CODE
		wallet_creator = _WalletCreator(self.session, user.id, currency_alpha_code=user_currency)
		wallet = wallet_creator.create_wallet()
		result = {}
		result['user'] = user
		result['wallet'] = wallet
		return result


	def _create_user_only(self):
		user_kwargs = self.kwargs
		password = user_kwargs.pop('password')
		curr = user_kwargs.get('default_currency_alpha_code')
		user = models.Users(**user_kwargs)

		user.set_password(password)
		logger.info("Attempting to create user. Name>>{}, email>>{}".format(user.name, user.email))
		try:
			logger.debug("Attempting to add user to session. Name>>{}, email>>{}"\
				.format(user.name, user.email))

			self.session.add(user)

			logger.debug("User added to session. Name>>{}, email>>{}"\
				.format(user.name, user.email))
			logger.debug("Attempting to persist changes. Name>>{}, email>>{}"\
				.format(user.name, user.email))

			self.session.commit()

			logger.debug("Changes persisted. Name>>{}, email>>{}"\
				.format(user.name, user.email))
		except Exception as e:
			#This bit essentially does nothing. Included in prep
			#For including more custom error reporting
			logger.error("Failed to create user Name>> {}, email>> {}.\
				See exception on next line\n{}".format(user.name, user.email, type(e)))
			
			raise e

		logger.info("Created user. ID>>{} Name>>{}, email>>{}"\
			.format(user.id, user.name, user.email))
		return user


class _WalletCreator:
	'''
	Functionality to create a wallet, to ultimately be associated with a user
	'''
	def __init__(self, session, ownerid, currency_alpha_code=DEFAULT_CURRENCY_ALPHA_CODE):
		self.ownerid = ownerid
		self.currency_alpha_code=currency_alpha_code
		self.session = session

	def create_wallet(self):
		'''
		Create a wallet with specified ownerid and currency
		'''
		wallet = models.Wallets(\
			ownerid=self.ownerid,
			currency_alpha_code=self.currency_alpha_code,
			balance=0)
		try:
			logger.info(\
				"Attempting to create wallet. ownerid>>{}, currency>>{}, balance>>{}"\
				.format(wallet.ownerid, wallet.currency_alpha_code, str(wallet.balance)))
			self.session.add(wallet)
			self.session.commit()
		except Exception as e:
			logger.error(\
				"Error creating wallet. ownerid>>{}, currency>>{}, balance>>{}.\
				See exception on next line\n{}"\
				.format(wallet.ownerid, wallet.currency_alpha_code, str(wallet.balance), str(e)))

		logger.info(\
				"Created wallet.walletid>>{}, ownerid>>{}, currency>>{}, balance>>{}"\
				.format(wallet.id, wallet.ownerid, wallet.currency_alpha_code, str(wallet.balance)))
		self.wallet = wallet
		return wallet


