from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import *


class StartForm(FlaskForm):
    submit = SubmitField("Готово")


class UserForm(StartForm):
    name = StringField('Логин', validators=[DataRequired("Пожалуйста введите Логин")])
    email = StringField('Почту', validators=[DataRequired("Пожалуйста введите Почту"), Email("Пожалуйста корректную Почту")])
    first_password = PasswordField('Введите пароль', validators=[DataRequired("Пожалуйста введите Пароль")])
    repeat_password = PasswordField('Повторите пароль', validators=[DataRequired("Пожалуйста повторите Пароль"), EqualTo('first_password', message='Пароли не совпадают')])
    remember = BooleanField("Запомнить меня")
    password = PasswordField('Пароль', validators=[DataRequired("Пожалуйста введите Пароль")])
