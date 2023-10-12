from flask import Blueprint, request, render_template, flash, redirect, url_for, abort
from flask_login import login_required, current_user

from blog_piligrim import db
from blog_piligrim.main.utils import save_picture
from blog_piligrim.models import Post, Comment, Like
from blog_piligrim.posts.forms import PostForm, CommentForm, LikeForm

posts = Blueprint('posts', __name__)


@posts.route("/allpost")
@login_required
def allpost():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('allpost.html', posts=posts)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    image_file = save_picture(form.picture.data, 'static/posts_pics') if form.picture.data else None
    if form.validate_on_submit():
        # image_file = save_picture(form.picture.data, 'static/post_pics') if form.picture.data else None
        post = Post(title=form.title.data, content=form.content.data, author=current_user, image_file=image_file)
        db.session.add(post)
        db.session.commit()
        flash("Ваш пост создан!")
        return redirect(url_for('posts.allpost'))
    return render_template('create_post.html', title='Новый пост', form=form, legend='Новый пост',
                           image_file=image_file)


@posts.route("/post/<string:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    like_form = LikeForm()
    like_count = Like.query.filter_by(post_id=post_id).count()
    if form.validate_on_submit():
        comment = Comment(body=form.comment.data, post_id=post_id, username=current_user.username)
        db.session.add(comment)
        db.session.commit()
        flash('Ваш комментарий добавлен', 'success')
        return redirect(f'/post/{post_id}')
    return render_template('post.html', title=post.title, post=post, form=form, like_form=like_form,
                           like_count=like_count)


@posts.route("/post/<string:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.image_file = save_picture(form.picture.data, 'static/posts_pics') if form.picture.data else post.image_file
        db.session.commit()
        flash("Ваша статья обновлена")
        return redirect(url_for("posts.post", post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    image_file = url_for('static', filename='posts_pics/' + post.image_file)
    return render_template('create_post.html', title='Обновление поста', form=form, legend='Обновление поста',
                           image_file=image_file)


@posts.route("/post/<string:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Ваша статья удалена")
    return redirect(url_for('posts.allpost'))


@posts.route("/comment/<string:comment_id>/delete", methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.username != current_user.username:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Ваш комментарий был удален', 'success')
    return redirect(url_for('posts.post', post_id=comment.post_id))


@posts.route('/post/<string:post_id>/like', methods=['POST', ])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author == current_user:
        flash('Вы не можете поставить лайк т.к. Вы - автор поста', 'warning')
    elif Like.query.filter_by(user_id=current_user.id, post_id=post_id).count():
        Like.query.filter_by(user_id=current_user.id, post_id=post_id).delete()
        db.session.commit()
        flash('Вам больше не нравится этот пост', 'success')
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        flash('Вам нравится этот пост', 'success')
    return redirect(url_for('posts.post', post_id=post_id))
