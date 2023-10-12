from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from blog_piligrim import create_app, db
from blog_piligrim.models import User, Post

app = create_app()
admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
