from .database import db

class Like(db.Model):
    __table_args__ = (db.PrimaryKeyConstraint('user_id', 'post_id', name='CompositePkForLike'),)
    user_id = db.Column(db.String(length=36), db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.String(length=36), db.ForeignKey('post.id'), nullable=False)
