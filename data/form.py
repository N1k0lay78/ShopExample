from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import StringField, SubmitField, PasswordField, BooleanField, FloatField


class YesNoFrom(FlaskForm):
    cancel = SubmitField("Нет")
    submit = SubmitField("Да")


class StartForm(FlaskForm):
    submit = SubmitField("Готово")


class AdminForm(FlaskForm):
    cancel = SubmitField("Отмена")
    submit = SubmitField("Применить")


class UserForm(StartForm):
    name = StringField('Логин', validators=[DataRequired("Пожалуйста введите Логин")])
    email = StringField('Почту',
                        validators=[DataRequired("Пожалуйста введите Почту"), Email("Пожалуйста корректную Почту")])
    first_password = PasswordField('Введите пароль', validators=[DataRequired("Пожалуйста введите Пароль")])
    repeat_password = PasswordField('Повторите пароль', validators=[DataRequired("Пожалуйста повторите Пароль"),
                                                                    EqualTo('first_password',
                                                                            message='Пароли не совпадают')])
    remember = BooleanField("Запомнить меня")
    password = PasswordField('Пароль', validators=[DataRequired("Пожалуйста введите Пароль")])


class ChangeAminForm(AdminForm):
    name = StringField('Логин', validators=[DataRequired("Пожалуйста введите Логин")])
    email = StringField('Почту',
                        validators=[DataRequired("Пожалуйста введите Почту"), Email("Пожалуйста корректную Почту")])
    first_password = PasswordField('Новый пароль', validators=[])
    repeat_password = PasswordField('Повторите пароль', validators=[EqualTo('first_password',
                                                                            message='Пароли не совпадают')])


# items
class ItemForm(AdminForm):
    name = StringField('Название', validators=[DataRequired("Пожалуйста введите Название")])
    short_description = StringField('Короткое описание', validators=[DataRequired("Пожалуйста введите Описание")])
    full_description = StringField('Полное описание', validators=[DataRequired("Пожалуйста введите Описание")])
    price = FloatField('Цена', validators=[DataRequired("Пожалуйста введите Цену")])
    type_item = StringField('Тип товара', validators=[DataRequired("Пожалуйста введите Тип товара")])
