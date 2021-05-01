import os
from flask_wtf import FlaskForm
from loko.models.models import SupportedCurrencies
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from loko.models import get_db_session, models

env = os.environ['FLASK_ENV']
session = get_db_session(env=env)
class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired(message= "Enter user name"),Length(min=3, message='Are you sure that\'s your name?')])
	username = StringField('Username', validators=[DataRequired(),Length(min=3, message='Please supply a longer username')])
	email = StringField('Email', validators=[DataRequired(), Email()])
	starting_balance =  DecimalField('Starting Balance', validators=[DataRequired(message="Please provide your account's starting balance. I know this sounds too good to be true ;)")])
	currency = SelectField('Currency', choices=[(cur.name, cur.name) for cur in list(SupportedCurrencies)])
	password = PasswordField('Password', validators=[DataRequired(),Length(min=5,message='Please supply a longer password')])
	password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
	accept_terms = BooleanField('I accept the terms of this site')
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = session.query(models.Users).filter_by(username=username.data.lower()).first()
		if user is not None:
			raise ValidationError('Invalid username. Please use a different username.')

	def validate_email(self, email):
		user = session.query(models.Users).filter_by(email=email.data.lower()).first()
		if user is not None:
			raise ValidationError('Invalid email address. Please use a different email address.')

	def validate_name(self, name):
		if name.data.startswith(' '):
			raise ValidationError('Invalid name. Cannot start with a space')

		if name.data.endswith(' '):
			raise ValidationError('Invalid name. Cannot end with a space')

		if ' ' not in name.data:
			raise ValidationError('Invalid name. Provide your forename and surname separated by a space')

class SendMoneyForm(FlaskForm):
	def set_default_currency(self,default_currency_alpha_code):
		for option in self.currency:
			if option._value() == default_currency_alpha_code:
				option.checked=True
				break

	recipient_email = StringField('Recipient\'s email', validators=[DataRequired(message="Enter receipient email")])
	amount = DecimalField('Amount', validators=[DataRequired(message="Enter amount you wish to send")])
	currency = SelectField('Currency', choices=[(cur.name, cur.name) for cur in list(SupportedCurrencies)])
	# narrative = StringField('Narrative', validators=[DataRequired(),Length(max=15, message='Narrative limited to 15 characters')])
	password = PasswordField('Password', validators=[DataRequired(message="Please Enter your password")])
