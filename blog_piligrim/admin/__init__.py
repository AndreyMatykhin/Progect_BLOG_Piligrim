from flask import redirect, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import current_user

from blog_piligrim.models import User, Post
from blog_piligrim.models.database import db


class CustomView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_staff

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("users.login"))


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        if not (current_user.is_authenticated and current_user.is_staff):
            return redirect(url_for('users.login'))
        return super(MyAdminIndexView, self).index()


class UserAdminView(CustomView):
    column_exclude_list = ("_password",)
    # column_searchable_list = ("first_name", "last_name", "username", "is_staff", "email")
    # column_filters = ("first_name", "last_name", "username", "is_staff", "email")
    # column_editable_list = ("first_name", "last_name", "is_staff")
    # can_create = False
    # can_edit = True
    # can_delete = False


admin = Admin(name="PILIGRIM-Blog Admin", index_view=MyAdminIndexView(), template_mode="bootstrap4")
admin.add_link(MenuLink(name='Home page My_Blog', url='/'))
admin.add_view(UserAdminView(User, db.session, category="Models"))
admin.add_view(ModelView(Post, db.session))
