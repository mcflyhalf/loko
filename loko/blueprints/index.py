import os
from sqlalchemy.exc import NoResultFound
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from loko.models import get_db_session
from loko.models.models import Users, SupportedCurrencies
from loko.forms import SendMoneyForm
from loko.models.db_utils import get_wallet_attrs_from_user
from loko.biz.transactor import TransactionCreator

index_blueprint = Blueprint('index_blueprint', __name__)
session = get_db_session(env=os.environ['FLASK_ENV'])

@index_blueprint.route('/')
@index_blueprint.route('/index/')
@login_required
def landing():
	wallet = get_wallet_attrs_from_user(session, current_user)
	smf = SendMoneyForm()
	smf.set_default_currency(wallet['currency_alpha_code'])
	# raise
	return render_template('index.html', wallet=wallet, sendmoney_form=smf)

#Potentially change to /modify/entity to allow deleting through this route as well
@index_blueprint.route('/sendmoney', methods=['POST'])
@login_required
def request_send_money():
	# print("Entity type: {}\nPayload: {}".format(entity_type,123))
	# return 'Received Form'
	#The error messages on this form are waaay more verbose than they should be
	#Doing this only for the benefit of interviewers.
	#Normally, these would be logged for internal consumption only
	#And a generic error message would be sent

	form = SendMoneyForm()
	if form.validate_on_submit():
		raw_pwd = form.password.data
		recipient_email = form.recipient_email.data
		amount = form.amount.data
		currency_alpha_code = form.currency.data
		#Check password
		if not current_user.check_password(raw_pwd):
			return jsonify({'status':'fail', 
							'Error':'Bad password'})

		#check recipient's existence
		try:
			recipient_user = (session.query(Users).
							filter(Users.email==recipient_email)
							.one())
		except NoResultFound:
			return jsonify({'status':'fail', 
					'Error':'Non-existent recipient email'})

		#Send money
		origin_wallet = get_wallet_attrs_from_user(session, current_user)
		destination_wallet = get_wallet_attrs_from_user(session, recipient_user)
		currency_enum = SupportedCurrencies[currency_alpha_code]
		 
		tx = TransactionCreator(session, origin_wallet['id'], current_user.id)
		try:
			tx_details = tx.send(float(amount), currency_enum, destination_wallet['id'], "narrative")
		except ValueError:
			return jsonify({'status':'fail', 
					'Error':'Invalid currency. Currency must be same as source or recipient'})

		response = {'status':'success'}
		response['transaction info'] = tx_details
		return jsonify(response)
	print("no form arrived")
	return jsonify({'status':'fail',
					'Error':'Unknown error'})