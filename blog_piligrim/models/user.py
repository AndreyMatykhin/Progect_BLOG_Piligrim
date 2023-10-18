from datetime import datetime, timezone, timedelta
import uuid

import flask_bcrypt
from flask import current_app
from jwt import encode, decode

from .database import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    # first_name = db.Column(db.String(120), unique=False, nullable=False, default="", server_default="")
    # last_name = db.Column(db.String(120), unique=False, nullable=False, default="", server_default="")
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar = db.Column(db.String(20), nullable=False, default='default.jpg')
    is_staff = db.Column(db.Boolean, nullable=False, default=False)
    _password = db.Column(db.LargeBinary, nullable=False)
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

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = flask_bcrypt.generate_password_hash(value)

    def validate_password(self, password) -> bool:
        return flask_bcrypt.check_password_hash(self._password, password)
