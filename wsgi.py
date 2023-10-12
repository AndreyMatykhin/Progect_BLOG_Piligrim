# from blog_piligrim import create_app
from blog_piligrim.admin import app

# app = create_app()


# @app.cli.command('init-db')
# def init_db():
#     db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
