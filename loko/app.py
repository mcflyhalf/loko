import os
from flask import Flask
from flask_login import LoginManager
from loko.blueprints.index import index_blueprint
from loko.blueprints.auth import auth_blueprint
from loko.models import get_db_session, models

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']
session = get_db_session(env=os.environ['FLASK_ENV'])

login_manager = LoginManager(app)
login_manager.init_app(app)

login_manager.login_view = 'auth_blueprint.login'

@login_manager.user_loader
def load_user(user_id):
    return session.query(models.Users).filter(models.Users.id==int(user_id)).one_or_none()


app.register_blueprint(index_blueprint)
app.register_blueprint(auth_blueprint)
