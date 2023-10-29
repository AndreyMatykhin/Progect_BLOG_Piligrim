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
    image_file = db.Column(db.String(20), nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    latitude = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'Запись {self.title}, {self.date_posted}'


def default_location():
    all_longitude = [el.longitude for el in Post.query.all() if el.longitude]
    all_latitude = [el.latitude for el in Post.query.all() if el.latitude]
    averge_longitude = sum(all_longitude)/len(all_longitude) if len(all_latitude) else 59.9391
    averge_latitude = sum(all_latitude)/len(all_latitude) if len(all_latitude) else 30.3155
    return averge_longitude, averge_latitude

