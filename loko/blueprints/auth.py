from flask import Blueprint, render_template, redirect, flash, url_for, request
from loko.blueprints.index import index_blueprint
from loko.models import session, models
from loko.forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse

auth_blueprint = Blueprint('auth_blueprint', __name__)

@auth_blueprint.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index_blueprint.landing'))
	form = LoginForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		user = session.query(models.Users).\
					  filter(models.Users.username == username.lower()).\
									  one_or_none()

		if user is None or not user.check_password(password):
			flash('Invalid username or password')
			return redirect(url_for('auth_blueprint.login'))
		
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index_blueprint.landing')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form, current_user=current_user)

@auth_blueprint.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index_blueprint.landing'))

@auth_blueprint.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index_blueprint.landing'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = models.Users(username=form.username.data.lower(), name=form.name.data, email=form.email.data,authenticated=False,active=True)
		user.set_password(form.password.data)
		session.add(user)
		session.commit()		
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('auth_blueprint.login'))
	return render_template('register.html', form=form, current_user=current_user, title='Register')

