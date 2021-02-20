"""Index views for login, logout and registration."""

from flask import request, flash, redirect, render_template, url_for
from flask_admin import AdminIndexView
from flask_login import current_user, login_user, logout_user

from web_shop import app, db
from web_shop.database.models import User, UserTypeChoices
from web_shop.forms import MyLoginForm, MyRegisterForm


@app.route("/")
def index():
    """Index view."""
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
        if request.args.get("next"):
            return redirect(url_for(request.args.get("next")))
        return redirect(url_for("index"))
    return render_template("login.html", title="Вход в учётную запись", form=form)


@app.route("/logout")
def logout():
    """Logout user route handler."""
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration route handler."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = MyRegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data)
        user.set_password(form.password.data)
        user.create_checking_token()
        user.user_type = getattr(UserTypeChoices, form.user_type.data).name
        db.session.add(user)
        db.session.commit()
        flash("Регистрация прошла успешно! Вы можете войти в личный кабинет.")
        return redirect(url_for("login"))

    return render_template("register.html", title="Регистрация", form=form)


class MyAdminIndexView(AdminIndexView):
    """Overrides access to admin index page."""

    def is_accessible(self):
        """Lets user enter admin view on condition."""
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        """Redirects user to login view on admin view entering if user is not logged in."""
        # redirect to login page if user doesn't have access
        return redirect(url_for("login", next="admin.index"))
