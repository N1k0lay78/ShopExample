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
    "admin_links": [
        ['/admin', 'панель администратора'],
    ],
}


def render_page(page: str, title, **kwargs):
    return render_template(page, title=title, data=data,
                           is_logined=not current_user.is_anonymous,
                           is_admin=not current_user.is_anonymous and current_user.access > 0,
                           **kwargs)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    return user


def login(login_form):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == login_form.email.data).first()
    session.close()
    if not user:
        return "нет такого пользователя"
    elif not user.check_password(login_form.password.data):
        return "неверный логин или пароль"
    else:
        login_user(user, remember=login_form.remember.data)
    return ""


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    form = UserForm()
    error = ""
    if request.method == 'POST':
        error = login(form)
        if error == "" and current_user.access < 1:
            return redirect('/')
        elif error == "":
            return redirect('/admin')
    return render_page('users/login.html', 'Логин', form=form, error=error)


def register(register_form):
    error = ""
    session = db_session.create_session()
    if session.query(User).filter(User.email == register_form.email.data).first():
        error = "Эта почта уже использовалась"
    elif session.query(User).filter(User.nickname == register_form.name.data).first():
        error = "Уже есть пользователь с таким именем"
    elif register_form.first_password.data != register_form.repeat_password.data:
        error = "Пароли не совпадают"
    elif len(register_form.first_password.data) < 8:
        error = "Длинна пароля менее 8 символов"
    elif register_form.first_password.data.isdigit():
        error = "В пароле нет буквы"
    elif register_form.first_password.data.isalpha():
        error = "В пароле нет цифры"
    else:
        new_user = User()
        new_user.nickname = register_form.name.data
        new_user.email = register_form.email.data
        new_user.set_password(register_form.first_password.data)
        session.add(new_user)
        session.commit()
    session.close()
    return error


@app.route('/register/', methods=['GET', 'POST'])
def register_page():
    form = UserForm()
    error = ""
    if request.method == 'POST':
        error = register(form)
        if error == "":
            return redirect('/login')
    return render_page('users/register.html', 'Регистрация', form=form, error=error)


@app.route('/logout/')
@login_required
def logout_page():
    logout_user()
    return redirect("/")


@app.route('/admin/')
@login_required
def admin_page():
    if current_user.access > 0:
        return render_page('admin/main.html', 'Панель администратора', admin=current_user)
    else:
        return redirect('/login')


@app.route('/')
def main_page():
    return render_page('users/main.html', 'Главная')


if __name__ == '__main__':
    app.run(port=8001)
