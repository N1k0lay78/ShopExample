import os
from random import choice
from flask import Flask, render_template, request
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from werkzeug.utils import redirect
from data import db_session
from data.item import Item
from data.type import Type
from data.user import User
from data.form import *
import config

db_session.global_init("db/my.sqlite")
app = Flask(__name__)
app.config.from_object(config)
login_manager = LoginManager()
login_manager.init_app(app)
let = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"


def create_random_name(name_len):
    return ''.join([choice(let) for _ in range(name_len)])


def delete_img(path, filename):
    if filename not in [""] and os.path.exists(path+filename):
        os.remove(path+filename)


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
        ['/admin', 'главная'],
        ['/admin/item', 'товары'],
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
    if get_admin(id_admin) and not upward_admin(current_user, id_admin):
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
    if get_admin(id_admin) and not upward_admin(current_user, id_admin):
        return redirect('/admin')
    form = YesNoFrom()
    if request.method == 'POST':
        if form.submit.data:
            admin_delete(id_admin)
        return redirect('/admin')
    return render_page('admin/delete.html', 'Удалить админа', form=form, type='admin', name=get_admin(id_admin).name)


def item():
    session = db_session.create_session()
    items = session.query(Item).all()
    return items, session


@app.route('/admin/item/', methods=['GET', 'POST'])
@login_required
def item_page():
    if current_user.access < 1:
        return redirect('/login')
    items, session = item()
    a = render_page('admin/item/main.html', 'Товары', items=items)
    session.close()
    return a


def item_add(add_item_form, file):
    session = db_session.create_session()
    error = ""
    if session.query(Item).filter(Item.name == add_item_form.name.data).first():
        error = "Товар с таким именем уже существует"
    elif not session.query(Type).filter(Type.type == add_item_form.type_item.data).first():
        error = "нет такого типа товара"
    else:
        new_item = Item()
        new_item.name = add_item_form.name.data
        new_item.short_description = add_item_form.short_description.data
        new_item.full_description = add_item_form.full_description.data
        filename = f'{create_random_name(50)}.{file.filename.split(".")[-1]}'
        file.save('static/img/item/'+filename)
        new_item.image = filename
        # print(float(add_item_form.price._value().replace(',', '.')), add_item_form.price)
        new_item.price = int(float(add_item_form.price._value().replace(',', '.')) * 100)
        new_item.type_id = session.query(Type).filter(Type.type == add_item_form.type_item.data).first().id
        session.add(new_item)
        session.commit()
    session.close()
    return error


@app.route('/admin/item/add/', methods=['GET', 'POST'])
@login_required
def item_add_page():
    if current_user.access < 1:
        return redirect('/login')
    form = ItemForm()
    error = ""
    if request.method == 'POST':
        error = item_add(form, request.files['file'])
        if error == "":
            return redirect('/admin/item')
    return render_page('admin/item/edit.html', 'Создать товар', form=form, action='create', name="", error=error)


def get_item(id_item):
    session = db_session.create_session()
    searched_item = session.query(Item).get(id_item)
    return searched_item, session


def item_change(id_item, change_item_form, file):
    session = db_session.create_session()
    error = ""
    change_item = session.query(Item).get(id_item)
    if (session.query(Item).filter(Item.name == change_item_form.name.data).first() and
            change_item_form.name.data != change_item.name):
        error = "Товар с таким именем уже существует"
    elif (not session.query(Type).filter(Type.type == change_item_form.type_item.data).first() and
          change_item_form.type_item.data != change_item.type.type):
        error = "нет такого типа товара"
    else:
        change_item.name = change_item_form.name.data
        change_item.short_description = change_item_form.short_description.data
        change_item.full_description = change_item_form.full_description.data
        if file.filename != '':
            delete_img('static/img/item/', change_item.image)
            filename = f'{create_random_name(50)}.{file.filename.split(".")[-1]}'
            file.save('static/img/item/'+filename)
            print('change to ' + filename)
            change_item.image = filename
        change_item.price = int(float(change_item_form.price._value().replace(',', '.')) * 100)
        change_item.type_id = session.query(Type).filter(Type.type == change_item_form.type_item.data).first().id
        session.commit()
    session.close()
    return error


@app.route('/admin/item/change/<int:id_item>', methods=['GET', 'POST'])
@login_required
def item_change_page(id_item):
    if current_user.access < 1:
        return redirect('/login')
    form = ItemForm()
    error = ""
    if request.method == 'POST':
        if form.submit.data:
            error = item_change(id_item, form, request.files['file'])
            if error == "":
                return redirect('/admin/item')
        else:
            return redirect('/admin/item')
    else:
        searched_item, session = get_item(id_item)
        form.name.data = searched_item.name
        form.short_description.data = searched_item.short_description
        form.short_description.data = searched_item.short_description
        form.full_description.data = searched_item.full_description
        form.price.data = f"{searched_item.price // 100}.{searched_item.price % 100}"
        form.type_item.data = searched_item.type.type
        session.close()
    return render_page('admin/item/edit.html', 'Изменить предмет', form=form, action='edit',
                       name=get_item_name(id_item), error=error)


def get_item_name(id_item):
    session = db_session.create_session()
    searched_item = session.query(Item).get(id_item)
    session.close()
    return searched_item.name


def item_delete(id_item):
    session = db_session.create_session()
    searched_item = session.query(Item).get(id_item)
    delete_img('static/img/item/', searched_item.image)
    session.delete(searched_item)
    session.commit()
    session.close()


@app.route('/admin/item/delete/<int:id_item>', methods=['GET', 'POST'])
@login_required
def item_delete_page(id_item):
    if current_user.access < 1:
        return redirect('/login')
    form = YesNoFrom()
    if request.method == 'POST':
        if form.submit.data:
            item_delete(id_item)
        return redirect('/admin/item')
    return render_page('admin/delete.html', 'Удалить админа', form=form, type='item', name=get_item_name(id_item))


def main():
    session = db_session.create_session()
    items = session.query(Item).all()
    return items, session


@app.route('/')
def main_page():
    items, session = main()
    a = render_page('users/main.html', 'Главная', items=items)
    session.close()
    return a


if __name__ == '__main__':
    app.run(port=8001)
