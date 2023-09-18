from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from blog_piligrim.config import Config
# from .models import User

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    print(__name__)
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    from blog_piligrim.main.routes import main
    from blog_piligrim.users.routes import users

    app.register_blueprint(main)
    app.register_blueprint(users)

    return app
