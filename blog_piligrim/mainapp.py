import os

from flask import Flask, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager

from .admin import admin
from .errors.handlers import errors
from .main.routes import main
from .models import User
from .models.database import db
from .posts.routes import posts
from .users.routes import users

login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

mainapp = Flask(__name__)

mainapp.register_blueprint(main)
mainapp.register_blueprint(users, url_prefix="/users")
mainapp.register_blueprint(posts, url_prefix="/posts")
mainapp.register_blueprint(errors)

cfg_name = os.environ.get("CONFIG_NAME") or "ProductionConfig"
# cfg_name = "DevConfig"
mainapp.config.from_object(f"blog_piligrim.configs.{cfg_name}")
print(__name__, cfg_name)
db.init_app(mainapp)
login_manager.init_app(mainapp)
bcrypt.init_app(mainapp)
migrate = Migrate(mainapp, db)
mail.init_app(mainapp)
admin.init_app(mainapp)


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).one_or_none()


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("users.login"))


@mainapp.cli.command('init-db')
def init_db():
    db.create_all()


@mainapp.cli.command('reinit-db')
def reinit_db():
    db.drop_all()
    db.create_all()


@mainapp.cli.command("create-admin")
def create_admin():
    from .models import User
    admin_user = User(username="admin", email='admin@default.com', is_staff=True)
    admin_user.password = os.environ.get("ADMIN_PASSWORD") or "adminpass"
    db.session.add(admin_user)
    db.session.commit()
    print("done! created admin:", admin_user)


@mainapp.cli.command("create-users")
def create_user():
    from .models import User
    import string, random
    for i in range(5):
        name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        create_user = User(username=name, email=f'{name}@default.com', password='1234567890')
        db.session.add(create_user)
        db.session.commit()
        print("done! created users:", create_user)


@mainapp.cli.command("create-posts")
def create_posts():
    from .models import User, Post
    import string, random
    authors = User.query.all()
    for author in authors:
        text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=170))
        create_post = Post(title=f'Article by {author.username}', user_id=author.id, content=text)
        db.session.add(create_post)
        db.session.commit()
        print("done! created article:", create_post)
