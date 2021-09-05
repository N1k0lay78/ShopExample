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
    "authorized_links": [
        ['/logout', 'разлогиниться'],
    ],
    "unauthorized_links": [
        ['/login', 'зарегестрироваться'],
    ],
    "admin_links": [
        ['/admin', 'панель администратора'],
    ],
    "admin_page": [
        ['/admin', 'главная']
    ],
}


def check_passwords(password_1, password_2):
    error = ""
    if len(password_1) < 8:
        error = "Длинна пароля менее 8 символов"
    elif password_1.isdigit():
        error = "В пароле нет буквы"
    elif password_1.isalpha():
        error = "В пароле нет цифры"
    elif password_1 != password_2:
        error = "Пароли не совпадают"
    return error


def render_page(page: str, title, **kwargs):
    return render_template(page, title=title, data=data,
                           authorized=not current_user.is_anonymous,
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


def register(register_form, access):
    error = ""
    session = db_session.create_session()
    if session.query(User).filter(User.email == register_form.email.data).first():
        error = "Эта почта уже использовалась"
    elif session.query(User).filter(User.nickname == register_form.name.data).first():
        error = "Уже есть пользователь с таким именем"
    elif check_passwords(register_form.first_password.data, register_form.repeat_password.data):
        error = check_passwords(register_form.first_password.data, register_form.repeat_password.data)
    else:
        new_user = User()
        new_user.nickname = register_form.name.data
        new_user.email = register_form.email.data
        new_user.access = access
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
        error = register(form, 0)
        if error == "":
            return redirect('/login')
    return render_page('users/register.html', 'Регистрация', form=form, error=error)


@app.route('/logout/')
@login_required
def logout_page():
    logout_user()
    return redirect("/")


# admins page
def upward_admin(current_admin, id_admin):
    session = db_session.create_session()
    searched_admin = session.query(User).filter(User.id == id_admin).first()
    session.close()
    return current_admin.access > searched_admin.access


def get_admin(id_admin):
    session = db_session.create_session()
    searched_admin = session.query(User).filter(User.id == id_admin).first()
    session.close()
    return searched_admin


def admin():
    session = db_session.create_session()
    admins = session.query(User).filter(User.access > 0).all()
    session.close()
    return admins


@app.route('/admin/')
@login_required
def admin_page():
    if current_user.access < 1:
        return redirect('/login')
    admins = admin()
    return render_page('admin/main.html', 'Панель администратора', current_admin=current_user, admins=admins)


@app.route('/admin/admin/register/', methods=['GET', 'POST'])
def admin_register_page():
    form = UserForm()
    error = ""
    if request.method == 'POST':
        error = register(form, 1)
        if error == "":
            return redirect('/admin')
    return render_page('users/register.html', 'Регистрация', form=form, error=error)


def admin_change(id_admin, change_admin_from):
    error = ""
    session = db_session.create_session()
    searched_admin = session.query(User).filter(User.id == id_admin).first()
    if (session.query(User).filter(User.email == change_admin_from.email.data).first() and
            change_admin_from.email.data != searched_admin.email):
        error = "Эта почта уже использовалась"
    elif (session.query(User).filter(User.nickname == change_admin_from.name.data).first() and
          change_admin_from.name.data != searched_admin.nickname):
        error = "Уже есть пользователь с таким именем"
    elif (check_passwords(change_admin_from.first_password.data, change_admin_from.repeat_password.data) and
          change_admin_from.first_password.data != ""):
        error = check_passwords(change_admin_from.first_password.data, change_admin_from.repeat_password.data)
    else:
        searched_admin.nickname = change_admin_from.name.data
        searched_admin.email = change_admin_from.email.data
        if change_admin_from.first_password.data != "":
            searched_admin.set_password(change_admin_from.first_password.data)
        session.commit()
    session.close()
    return error


@app.route('/admin/admin/change/<int:id_admin>', methods=['GET', 'POST'])
@login_required
def admin_change_page(id_admin):
    if current_user.access < 1:
        return redirect('/login')
    if not upward_admin(current_user, id_admin):
        return redirect('/admin')
    form = ChangeAminForm()
    error = ""
    if request.method == 'POST':
        if form.submit.data:
            error = admin_change(id_admin, form)
            if error == "":
                return redirect('/admin')
        else:
            return redirect('/admin')
    else:
        searched_admin = get_admin(id_admin)
        form.name.data = searched_admin.nickname
        form.email.data = searched_admin.email
    return render_page('admin/admin/change.html', 'Изменить админа', form=form, admin=get_admin(id_admin), error=error)


def admin_delete(id_admin):
    session = db_session.create_session()
    searched_admin = session.query(User).filter(User.id == id_admin).first()
    session.delete(searched_admin)
    session.commit()
    session.close()


@app.route('/admin/admin/delete/<int:id_admin>', methods=['GET', 'POST'])
@login_required
def admin_delete_page(id_admin):
    if current_user.access < 1:
        return redirect('/login')
    if not upward_admin(current_user, id_admin):
        return redirect('/admin')
    form = YesNoFrom()
    if request.method == 'POST':
        if form.submit.data:
            admin_delete(id_admin)
        return redirect('/admin')
    return render_page('admin/admin/delete.html', 'Удалить админа', form=form, admin=get_admin(id_admin))


@app.route('/')
def main_page():
    return render_page('users/main.html', 'Главная')


if __name__ == '__main__':
    app.run(port=8001)
