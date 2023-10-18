from flask import Blueprint, redirect, url_for, flash, render_template, request, current_app
from flask_login import current_user, login_user, login_required, logout_user, LoginManager

from ..mainapp import db
from ..main.utils import save_picture
from ..models import User, Post
from ..users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, \
    ResetPasswordForm
from ..users.utils import send_reset_email

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Ваша учетная запись была создана! Можете войти в систему.')
        return redirect(url_for('users.login'))
    return render_template('users/register.html', title='Register', form=form)


@users.route("login", methods=['GET', 'POST'], endpoint='login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.validate_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Войти не удалось. Проверьте электронную почту и пароль.')
    return render_template('users/login.html', title='Авторизация', form=form)


@users.route("/users_update", methods=['GET', 'POST'])
@login_required
def users_update():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'static/profile_pics')
            current_user.avatar = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Ваш аккуаунт был обновлен')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        page = request.args.get('page', 1, type=int)
        user = User.query.filter_by(username=form.username.data).first_or_404()
        posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    image_file = url_for('static', filename='profile_pics/' + current_user.avatar)
    return render_template('users/users_update.html', title='Профиль', image_file=image_file, form=form, posts=posts,
                           user=user)


@users.route("/account/<string:user_id>")
@login_required
def account(user_id):
    user = User.query.get_or_404(user_id)
    image_file = url_for('static', filename='profile_pics/' + user.avatar)
    return render_template('users/account.html', title=user.username, image_file=image_file, user=user)


@users.route("/allusers")
@login_required
def allusers():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.username).paginate(page=page, per_page=5)
    return render_template('users/users_list.html', users=users,context_title='Все пользователи')


@users.route("/allathors")
def allathors():
    page = request.args.get('page', 1, type=int)
    authors = {post.user_id for post in Post.query.all()}
    users = User.query.filter(User.id.in_(authors)).order_by(User.username).paginate(page=page, per_page=5)
    return render_template('users/users_list.html', users=users,context_title='Список авторов')


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('post.allposts'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('На Вашу почту отправлено письмо с инструкцией по сбросу пароля', 'info')
        return redirect(url_for('users.login'))
    return render_template('users/reset_request.html', title='Сброс пароля', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('post.allpost'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("Это недействительный или просроченный токен", 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flash("Ваш пароль был обновлен! Теперь вы можете авторизоваться.", "success")
        return redirect(url_for('users.login'))
    return render_template('users/reset_token.html', title='Сброс пароля.', form=form)
