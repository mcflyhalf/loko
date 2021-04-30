from flask import Blueprint, render_template
from flask_login import login_required

index_blueprint = Blueprint('index_blueprint', __name__)

@index_blueprint.route('/')
@index_blueprint.route('/index/')
@login_required
def landing():
	return render_template('index.html')

