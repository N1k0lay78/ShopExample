from flask import Flask, render_template, request
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from werkzeug.utils import redirect
from data import db_session
from data.user import User
from data.form import *
import config

db_session.global_init("db/my.sqlite")
app = Flask(__name__)
app.config.from_object(config)
login_manager = LoginManager()
login_manager.init_app(app)

data = {
    "pages_links": [
        ['/', 'главная'],
        ['/item/1', 'товар номер 1'],
    ],
    "logined_links": [
        ['/logout', 'разлогиниться'],
    ],
    "unlogined_links": [
        ['/login', 'зaлогиниться'],
    ],
}


def register(login_form):
    error = ""
    session = db_session.create_session()
    if session.query(User).filter(User.email == login_form.email.data).first():
        error = "Эта почта уже использовалась"
    elif session.query(User).filter(User.nickname == login_form.name.data).first():
        error = "Уже есть пользователь с таким именем"
    elif login_form.first_password.data != login_form.repeat_password.data:
        error = "Пароли не совпадают"
    elif len(login_form.first_password.data) < 8:
        error = "Длинна пароля менее 8 символов"
    elif login_form.first_password.data.isdigit():
        error = "В пароле нет буквы"
    elif login_form.first_password.data.isalpha():
        error = "В пароле нет цифры"
    else:
        new_user = User()
        new_user.nickname = login_form.name.data
        new_user.email = login_form.email.data
        new_user.set_password(login_form.first_password.data)
        session.add(new_user)
        session.commit()
    session.close()
    return error


def render_page(page: str, title, **kwargs):
    return render_template(page, title=title, data=data, logined=not current_user.is_anonymous, **kwargs)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    return user


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    form = UserForm()
    if request.method == 'POST':
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        session.close()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect('/')
        else:
            print("nope", user)
    return render_page('users/login.html', 'Логин', form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register_page():
    form = UserForm()
    errors = ""
    if request.method == 'POST':
        errors = register(form)
        if errors == "":
            return redirect('/login')
    return render_page('users/register.html', 'Регистрация', form=form, errors=errors)


@app.route('/')
def main_page():
    return render_page('users/main.html', 'Главная')


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(port=8001)
