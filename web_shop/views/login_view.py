"""Login views."""
from datetime import timedelta

from flask import (
    Response,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_jwt_extended import create_access_token
from flask_login import current_user, login_user

from web_shop.database import User
from web_shop.forms import MyLoginForm
from web_shop import app


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login route handler."""
    if current_user.is_authenticated:
        return make_response(redirect(url_for("index")))

    form = MyLoginForm()
    if form.is_submitted():
        if not form.email.data and not form.password.data:
            flash("Адрес и пароль не указаны")
            return make_response(redirect(url_for("login")))

        if not form.email.data:
            flash("Адрес не указан")
            return make_response(redirect(url_for("login")))

        if not form.password.data:
            flash("Пароль не указан")
            return make_response(redirect(url_for("login")))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None:
            flash("Пользователь не зарегистрирован")
            return make_response(redirect(url_for("login")))

        if not user.check_password(form.password.data):
            flash("Ошибка при вводе пароля")
            return make_response(redirect(url_for("login")))

        if not user.confirmed_at:
            flash("Проверьте почту и активируйте учётную запись")
            return make_response(redirect(url_for("index")))

        login_user(user, remember=form.remember_me.data, force=True)

        if request.args.get("next"):
            resp: Response = make_response(redirect(url_for(request.args.get("next"))))
        else:
            resp: Response = make_response(redirect(url_for("index")))

        return resp

    return make_response(
        render_template("login.html", title="Вход в учётную запись", form=form)
    )
