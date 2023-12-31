from flask import Blueprint, request, render_template, flash, redirect, url_for, abort
from flask_login import login_required, current_user
import folium

from ..mainapp import db
from ..main.utils import save_picture, LatLngPopup
from ..models import Post, Comment, Like
from ..models.post import default_location
from ..posts.forms import PostForm, CommentForm, LikeForm

posts = Blueprint('posts', __name__)


@posts.route("/allposts_list")
def allposts_list():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('post/allposts_list.html', posts=posts)


@posts.route("/allposts_map")
def allposts_map():
    post_map = folium.Map(location=[*default_location()], zoom_start=6)
    geo_posts = [el for el in Post.query.all() if el.longitude and el.latitude]
    for post in geo_posts:
        print("<a href=\'{{ url_for(\'posts.post\', post_id=\'"+post.id +"\') }}\'>"+post.title+"</a>")
        folium.Marker(location=[post.longitude, post.latitude],
                      popup=folium.Popup(f"""<a href="/posts/post/{post.id}" target="_top">{post.title}</a>"""),
                      tooltip=post.title
                      ).add_to(post_map)
    post_map = post_map.get_root()._repr_html_()
    return render_template('post/allposts_map.html', post_map=post_map)


@posts.route("/allposts_of_user/<string:user_id>")
def allposts_of_user(user_id):
    user = Post.query.filter_by(user_id=user_id).first()
    if user:
        username = user.author.username
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(user_id=user_id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        return render_template('post/allposts_of_user.html', posts=posts, user=username)
    else:
        flash("У автора пока нет статей")
        return redirect(url_for('posts.allposts_list'))


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    image_file = save_picture(form.picture.data, 'static/posts_pics') if form.picture.data else None
    post_map = folium.Map(location=[*default_location()], zoom_start=8)
    post_map.add_child(LatLngPopup())
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user, image_file=image_file,
                    latitude=form.latitude.data, longitude=form.longitude.data)
        db.session.add(post)
        db.session.commit()
        print(form.latitude.id, form.latitude.data)
        print(form.longitude.id, form.longitude.data)
        flash("Ваш пост создан!")
        return redirect(url_for('posts.allposts_list'))
    return render_template('post/create_post.html', title='Новый пост', form=form, legend='Новая статья',
                           image_file=image_file, post_map=post_map.get_root()._repr_html_())


@posts.route("/post/<string:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.longitude and post.latitude:
        post_map = folium.Map(location=[post.longitude, post.latitude], zoom_start=12)
        folium.Marker(location=[post.longitude, post.latitude], popup=post.title, icon=folium.Icon(color='red')).add_to(
            post_map)
        post_map = post_map.get_root()._repr_html_()
    else:
        post_map = None
    form = CommentForm()
    like_form = LikeForm()
    like_count = Like.query.filter_by(post_id=post_id).count()
    if form.validate_on_submit():
        comment = Comment(body=form.comment.data, post_id=post_id, username=current_user.username)
        db.session.add(comment)
        db.session.commit()
        flash('Ваш комментарий добавлен', 'success')
        return redirect(f'/posts/post/{post_id}')
    return render_template('post/post.html', title=post.title, post=post, form=form, like_form=like_form,
                           like_count=like_count, post_map=post_map)


@posts.route("/post/<string:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if post.longitude and post.latitude:
        post_map = folium.Map(location=[post.longitude, post.latitude], zoom_start=12)
        folium.Marker(location=[post.longitude, post.latitude], popup=post.title, icon=folium.Icon(color='red')).add_to(
            post_map)
    else:
        post_map = folium.Map(location=[*default_location()], zoom_start=8)
    post_map.add_child(LatLngPopup())
    post_map = post_map.get_root()._repr_html_()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.latitude = form.latitude.data
        post.longitude = form.longitude.data
        post.image_file = save_picture(form.picture.data, 'static/posts_pics') if form.picture.data else post.image_file
        db.session.commit()
        flash("Ваша статья обновлена")
        return redirect(url_for("posts.post", post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        image_file = url_for('static', filename='posts_pics/' + post.image_file) if post.image_file else None
    return render_template('post/create_post.html', title='Обновление поста', form=form, legend='Обновление поста',
                           image_file=image_file, post_map=post_map)


@posts.route("/post/<string:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Ваша статья удалена")
    return redirect(url_for('posts.allposts_list'))


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
