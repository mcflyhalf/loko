from loko.models.models import Wallets, SupportedCurrencies


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