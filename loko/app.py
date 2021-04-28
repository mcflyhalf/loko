import os
from flask import Flask
# from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from loko.blueprints.index import index_blueprint
from loko.blueprints.auth import auth_blueprint
from loko.models import session

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']


app.register_blueprint(index_blueprint)
app.register_blueprint(auth_blueprint)
