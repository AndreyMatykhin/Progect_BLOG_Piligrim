from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from blog_piligrim.config import Config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    print(__name__)
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    from blog_piligrim.main.routes import main
    app.register_blueprint(main)
    return app
