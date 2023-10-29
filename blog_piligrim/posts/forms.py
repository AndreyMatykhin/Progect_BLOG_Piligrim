from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, FileField, FloatField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Текст', validators=[DataRequired()])
    picture = FileField('Приложите фото', validators=[FileAllowed(['jpg', 'png'])])
    latitude = FloatField("Широта")
    longitude = FloatField("Долгота")
    submit = SubmitField('Сохранить')


class CommentForm(FlaskForm):
    comment = StringField('Комментарий', validators=[DataRequired()])


class LikeForm(FlaskForm):
    submit = SubmitField('ЛЮБО!!!')
