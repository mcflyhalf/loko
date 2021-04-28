import os
from flask import Flask
from flask_login import LoginManager
from loko.blueprints.index import index_blueprint
from loko.blueprints.auth import auth_blueprint
from loko.models import session, models

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']

login_manager = LoginManager(app)
login_manager.init_app(app)

login_manager.login_view = 'auth_blueprint.login'

@login_manager.user_loader
def load_user(user_id):
    return session.query(models.Users).filter(models.Users.id==int(user_id)).one_or_none()


raise
#Next, implement business logic:
# * Wallet creation
# * Transfer from a wallet to another
# * Wallet balance display (working with decimal points)
# * Currency List
# * Exchange rates (table?). Do implementation research, to implement tomorrow


app.register_blueprint(index_blueprint)
app.register_blueprint(auth_blueprint)
