import os
from loko.biz.creator import UserCreator
from loko.biz.xchange import get_xchange_data, save_xchange_data
from loko.utils import get_configs
from loko.models.models import Users, Wallets, SupportedCurrencies


def populate_db(session, xchange_response_file):
	'''
	Populates db with dummy data to start off the application
	'''
	# Populate Currencies table
	xchange_data = get_xchange_data(xchange_response_file)
	save_xchange_data(xchange_data, session=session, save_to_db=True)
	sup_cur_list = list(SupportedCurrencies)
	tot_cur = len(sup_cur_list)

	# Populate Users and Wallets table. Each user gets a corresponding wallet
	for _id in range(1,7):
		usr = {}
		usr['id'] = _id
		
		usr['username'] = 'dev'+str(_id)
		usr['password'] = 'dev123'
		usr['name'] = 'Develo Per'+str(_id)
		usr['email'] = 'dev{}@dev.mail'.format(str(_id))
		usr['authenticated'] = False
		usr['active'] = True
		alpha_code = sup_cur_list[(_id+4)%tot_cur].name
		usr['default_currency_alpha_code'] = alpha_code
		wallet_balance = 1000

		usercreator = UserCreator(session, **usr)
		user_and_wallet = usercreator.create_user()
		wallet = user_and_wallet['wallet']
		wallet.balance = wallet_balance
		wallet.id = _id
		session.flush()

	session.commit()




