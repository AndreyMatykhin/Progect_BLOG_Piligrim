from flask import url_for
from flask_mail import Message, Mail

# from blog_piligrim.mainapp import mail
mail = Mail()


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Запрос на сброс пароля', sender='blog.piligrim@gmail.com', recipients=[user.email])
    msg.body = (f'Чтобы сбросить пароль, перейдите по следующей ссылке: '
                f'{url_for("users.reset_token", token=token, _external=True)}. Если вы не делали этот запрос'
                f'тогда просто проигнорируйте это письмои никаких изменений не будет.')
    mail.send(msg)
