"""Registration view."""
from flask import flash, make_response, redirect, render_template, url_for
from flask_login import current_user

from web_shop.utils.utils import create_link
from web_shop import app, db
from web_shop.database import User, UserTypeChoices
from web_shop.emails import (
    create_message,
    send_message,
)
from web_shop.forms import MyRegisterForm


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration route handler."""
    if current_user.is_authenticated:
        return make_response(redirect(url_for("index")))

    form = MyRegisterForm()

    if form.cancel.data:
        return make_response(redirect(url_for("index")))

    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password=form.password.data,
            user_type=getattr(UserTypeChoices, form.user_type.data).name,
        )
        db.session.add(user)
        db.session.commit()

        link = create_link(user.email)
        message = create_message("Подтверждение регистрации", user.email)
        message.html = (
            f"Для подтверждения учётной записи на WebShop перейдите по ссылке: {link}"
        )
        send_message(message)

        flash(
            "Регистрация прошла успешно! "
            "Проверьте вашу почту и подтвердите учётную запись в течение 1 минуты."
        )
        return make_response(redirect(url_for("index")))

    return make_response(render_template("register.html", title="Регистрация", form=form))
