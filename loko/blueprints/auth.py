from flask import Blueprint

auth_blueprint = Blueprint('auth_blueprint', __name__)

@auth_blueprint.route('/login')
def landing():
	return 'Hello World'


@auth_blueprint.route('/logout')
def landing():
	return 'Hello World'

