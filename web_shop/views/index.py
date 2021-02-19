"""Index view.

In future shall redirect to ROOT_URL.
"""

from flask import request, flash, redirect, render_template, url_for
from flask_login import current_user, login_user

from web_shop import app, db
from web_shop.database.models import User
from web_shop.forms import MyLoginForm, MyRegisterForm


@app.route("/")
def index():
    """Index view."""
    print(111, request.cookies)
    print(111, request.headers)
    print(111, request.values)

    return render_template("base.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login route handler."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = MyLoginForm()

    if form.is_submitted():
        if not form.email.data and not form.password.data:
            flash("Адрес и пароль не указаны")
            return redirect(url_for("login"))
        if not form.email.data:
            flash("Адрес не указан")
            return redirect(url_for("login"))
        if not form.password.data:
            flash("Пароль не указан")
            return redirect(url_for("login"))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("Пользователь не зарегистрирован")
            return redirect(url_for("login"))
        if not user.check_password(form.password.data):
            flash("Ошибка при вводе адреса почты или пароля")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("index"))

    return render_template("login.html", title="Вход в учётную запись", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration route handler."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = MyRegisterForm()
    if form.is_submitted():
        if not (
            form.email.data
            and form.password.data
            and form.password_confirm.data
            and form.last_name.data
            and form.first_name.data
        ):
            flash("Все поля обязательны к заполнению")
            return redirect(url_for("register"))

        if form.password.data != form.password_confirm.data:
            flash("Пароли не совпадают")
            return redirect(url_for("register"))

        if User.query.filter_by(email=form.email.data).first():
            flash("Данный адрес электронной почты уже используется")
            return redirect(url_for("register"))

        user = User(email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data)
        user.set_password(form.password.data)
        user.create_checking_token()
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))

    return render_template("register.html", title="Регистрация", form=form)
