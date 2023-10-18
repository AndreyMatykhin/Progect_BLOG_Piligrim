from datetime import datetime
import uuid

from .database import db


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

