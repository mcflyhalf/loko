from flask import Blueprint
from loko.models import current_user

index_blueprint = Blueprint('index_blueprint', __name__)

@index_blueprint.route('/')
@index_blueprint.route('/index/')
def landing():
	return 'Hello World'

