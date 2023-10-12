from datetime import datetime, timezone, timedelta
import uuid

from flask import current_app
from jwt import encode, decode

from blog_piligrim import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(str(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar = db.Column(db.String(20), nullable=False, default='default.jpg')
    is_staff = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f'Пользователь {self.username}, {self.email}, {self.avatar}'

    def get_reset_token(self, expires_sec=1800):
        payload = {'user_id': self.id, 'exp': datetime.now(timezone.utc) + timedelta(seconds=expires_sec)}
        return encode(payload, current_app.config["SECRET_KEY"], algorithm='HS256')

    @staticmethod
    def verify_reset_token(token, leeway=10):
        try:
            data = decode(token, current_app.config["SECRET_KEY"], leeway=leeway, algorithms='HS256')
        except Exception:
            return None
        return User.query.get(data['user_id'])


class Post(db.Model):
    id = db.Column(db.String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.String(length=36), db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='title', lazy='select', cascade='all, delete-orphan')
    image_file = db.Column(db.String(20), nullable=False, default='default.png')

    def __repr__(self):
        return f'Запись {self.title}, {self.date_posted}'


class Comment(db.Model):
    id = db.Column(db.String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    body = db.Column(db.String(length=140))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.String(length=36), db.ForeignKey('post.id'), nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)


class Like(db.Model):
    __table_args__ = (db.PrimaryKeyConstraint('user_id', 'post_id', name='CompositePkForLike'),)
    user_id = db.Column(db.String(length=36), db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.String(length=36), db.ForeignKey('post.id'), nullable=False)
