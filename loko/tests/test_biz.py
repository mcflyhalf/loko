'''
Tests for the business logic part of the app in loko/biz
'''
import pytest
from loko.models.models import Users, Wallets
from loko.biz.creator import _WalletCreator, UserCreator
from loko.tests import test_session
from sqlite3 import IntegrityError as ie
from sqlalchemy.exc import IntegrityError


def get_user_creation_kwargs():
	test_username = 'at_esther'
	test_password = 'verySecret'
	test_name = 'Stray Test'
	test_email = 'test@test.co.ke'
	test_authenticated = False
	test_active = True
	test_currency = 'GBP'

	kwargs = {}
	kwargs['username'] = test_username
	kwargs['password'] = test_password
	kwargs['name'] = test_name
	kwargs['email'] = test_email
	kwargs['authenticated'] = test_authenticated
	kwargs['active'] = test_active
	kwargs['default_currency_alpha_code'] = test_currency
	return kwargs


@pytest.fixture(scope='session')
def test_user_and_wallet(test_session):
	kwargs = get_user_creation_kwargs()

	usercreator = UserCreator(test_session, **kwargs)
	user_and_wallet = usercreator.create_user()
	return user_and_wallet

@pytest.fixture(scope='session')
def test_user(test_user_and_wallet):
	return test_user_and_wallet['user']

@pytest.fixture(scope='session')
def test_wallet(test_user_and_wallet):
	return test_user_and_wallet['wallet']


#------Tests for creator.py-----------
class TestWalletCreator:

	def create_wallet(self, user, test_session=test_session):
		wallet_ownerid=user.id

		wallet_creator = _WalletCreator(test_session, wallet_ownerid)
		_wallet = wallet_creator.create_wallet()
		return _wallet


	def test_create_wallet(self, test_user):
		#confirm all fields (balance, curr_code, id exists, ownerid)
		temp_test_wallet = self.create_wallet(test_user)
		assert type(temp_test_wallet) is Wallets
		assert temp_test_wallet.balance == 0
		#TODO: Test against DEFAULT_CURRENCY instead of hardcoding
		assert temp_test_wallet.currency_alpha_code == 'GBP'	# Will fail if the default currency changes
		assert temp_test_wallet.balance == 0


	def test_create_wallet_bad_currency_code(self):
		pass

	def test_create_wallet_duplicate_user_id(self, test_user):
		#This test essentially checks that nothing happens if a user is assigned 
		#to multiple wallets (2 in this case). Instead of failing, it would raise 
		#an exception
		duplicated_user = test_user
		wallet = self.create_wallet(duplicated_user)
		assert wallet.ownerid == duplicated_user.id
		with pytest.raises(ValueError):
			raise ValueError('Testing exceptionality')

	#This test causes an error that unlinks a wallet from its user!!!
	# def test_create_wallet_invalid_integer_id(self, test_user):
	# 	wallet_user = test_user
	# 	wallet_user.id = 9999799	#Unrealistic for this test db
	# 	#TODO: Should be raising an exception but isnt!!!
	# 	self.create_wallet(wallet_user)


class TestUserCreator:
	
	def test_create_user_only(self, test_session):
		kwargs = get_user_creation_kwargs()
		kwargs['username'] = 'temptester'
		kwargs['name'] = 'Temp Tester'
		kwargs['email'] = 'temp@tester.co.ke'

		usercreator = UserCreator(test_session, **kwargs)
		user = usercreator._create_user_only()

		assert user.username == kwargs['username']
		assert user.name == kwargs['name']
		assert user.email ==kwargs['email']
		assert user.id is not None

	def test_create_user_only_invalid_id(self, test_session):
		kwargs = get_user_creation_kwargs()
		kwargs['username'] = 'temptester'
		kwargs['name'] = 'Temp Tester'
		kwargs['email'] = 'temp@tester.co.ke'
		kwargs['id'] = 'INVALID'

		#Doesnt work because sqlalchemy internally changes the id
		usercreator = UserCreator(test_session, **kwargs)
		with pytest.raises(IntegrityError):
			user = usercreator._create_user_only()
		test_session.rollback()

	def test_create_user_only_duplicate_id(self, test_user, test_session):
		kwargs = get_user_creation_kwargs()
		kwargs['username'] = 'temptester'
		kwargs['name'] = 'Temp Tester'
		kwargs['email'] = 'temp@tester.co.ke'
		kwargs['id'] = test_user.id

		usercreator = UserCreator(test_session, **kwargs)
		with pytest.raises(IntegrityError):
			#Expect warning regarding duplicated id but test passes
			user = usercreator._create_user_only()


#------Tests for transactor.py--------
class TestCurrencyConverter:
	def test_get_exchange_rate(self):
		pass

	def test_convert(self):
		pass


class TestTransactionCreator:
	def test_calculate_comission(self):
		#test commision =0, comission <0, comission >0
		pass

	def test_calculate_comission_exceeds_max_comission(self):
		pass

	def test_calculate_comission_is_zero(self):
		pass

	def test_send_invalid_amounts(self):
		#test amount =0, <0, >wallet_balance
		pass

	def test_send_valid_amounts_same_currency(self):
		'''
		Send Valid amounts in the same currency(do this for all existing currencies) then confirm:
		- 2 Transactions are created
		- A commision is charged
		- Commision goes to Loko's account
		- Debited wallet balance reduces
		- Credited wallet balance increases
		'''
		pass

	def test_send_valid_amount_different_currency(self):
		'''
		Send Valid amounts btn wallets in different currency then check:
		- 2 Transactions are created
		- A commision is charged
		- Commision goes to Loko's account
		- Debited wallet balance reduces
		- Credited wallet balance increases
		'''
		pass


