'''
Gets exchange rate info from online api.
Currently uses Euro as base currency
'''
import os
import requests
import pickle
from sqlalchemy.orm.exc import NoResultFound
from loko.conf import get_configs
from loko.models.models import SupportedCurrencies, Currencies

XCHANGE_FILENAME_BASE = 'Xchange_data'

config = get_configs()

# XCHANGE_ENDPOINT = 'https://api.ratesapi.io/api/latest'
def upsert_currency(currency, session):
	'''
	An Upsert function that modifies the exchange rate ONLY if currency exists or creates a new one if none does
	Postgres has this method defined and we would switch to that if this is becoming a problem
	Currently, Exchange rates only change once a day
	'''
	try:
		q = session.query(Currencies).filter_by(alphabetic_code= currency.alphabetic_code)
		existing_currency = q.one()
	except NoResultFound:
		#currency does not exist yet
		session.add(currency)
	else:
		#currency already exists.  Make sure the values are what we want
		assert isinstance(existing_currency, Currencies)
		existing_currency.xchange_rate = currency.xchange_rate
	session.flush()


def _save_xchange_data_to_db(xchange_data, session):
	change_data = xchange_data
	base = xchange_data['base']

	#Include the Base currency
	change_data['rates'][base] = 1.0

	rate = change_data['rates']

	for currency_code in rate:
		currency = Currencies()
		currency.alphabetic_code = currency_code
		currency.xchange_rate = rate[currency_code]
		currency.minor_unit = SupportedCurrencies[currency_code].value['minor unit']
		currency.name = SupportedCurrencies[currency_code].value['common name']
		upsert_currency(currency, session)


def _save_xchange_data_to_file(xchange_data, path=None):
	if path is None:
		path = config['exchange rate file location']
	date = xchange_data['date']
	data = str(xchange_data)
	filename = XCHANGE_FILENAME_BASE+'_'+date+'.txt'
	filepath = os.path.join(path,filename)
	with open(filepath, 'w') as f:
		f.write(data + '\n')


def get_xchange_data(endpoint_or_filepath):

	url_params = {}
	sup_curr = list(SupportedCurrencies)
	supported_currency_codes = [curr.name for curr in sup_curr]
	#Get the base and remove it from the list
	#API throws error if exchange rate for base is requested
	url_params['base'] = supported_currency_codes.pop(0)
	url_params['symbols']= ','.join(supported_currency_codes)
	
	# resp = requests.get(endpoint, params=url_params)
	with open(endpoint_or_filepath,'rb') as f:
		resp=pickle.load(f)

	if resp.status_code != 200:
		raise ValueError('Error getting currency data from{}'.format(endpoint))

	return resp.json()

def save_xchange_data(xchange_data, path=None,session=None,save_to_db=False):
	'''
	Save exchange rate data from a dict to a file or to the db
	:param xchange_data: dict containing the exchange rate data in the format from get_xchange_data
	:param path: path of the file to save data to. Required when saving to file
	:param session: db session to use to save data to db. Required when db is True
	:param save_to_db: When true, save to db (via session), when false, save to file
	'''
	if save_to_db:
		_save_xchange_data_to_db(xchange_data, session)
	else:
		_save_xchange_data_to_file(xchange_data)

#Testing code...
if __name__ == '__main__':
	from loko.models import get_db_session
	session = get_db_session()
	xchange_data = get_xchange_data('../../example_xchange_resp9.pkl')
	save_xchange_data(xchange_data, session=session, save_to_db=True)


