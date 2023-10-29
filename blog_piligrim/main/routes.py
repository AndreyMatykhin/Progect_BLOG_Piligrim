from flask import render_template, Blueprint
import folium

from ..models.post import default_location, Post

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    post_map = folium.Map(location=[*default_location()], zoom_start=6)
    geo_posts = [el for el in Post.query.all() if el.longitude and el.latitude]
    for post in geo_posts:
        print("<a href=\'{{ url_for(\'posts.post\', post_id=\'" + post.id + "\') }}\'>" + post.title + "</a>")
        folium.Marker(location=[post.longitude, post.latitude],
                      popup=folium.Popup(f"""<a href="/posts/post/{post.id}" target="_top">{post.title}</a>"""),
                      tooltip=post.title
                      ).add_to(post_map)
    post_map = post_map.get_root()._repr_html_()
    return render_template('index.html', post_map=post_map)
