from flask import Blueprint

index_blueprint = Blueprint('index_blueprint', __name__)

@index_blueprint.route('/')
@index_blueprint.route('/index/')
def landing():
	return 'Hello World'

