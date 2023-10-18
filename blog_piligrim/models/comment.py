from datetime import datetime
import uuid

from .database import db


class Comment(db.Model):
    id = db.Column(db.String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    body = db.Column(db.String(length=140))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.String(length=36), db.ForeignKey('post.id'), nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
