"""View for confirmation emails and tokens."""
import random
from datetime import datetime
from string import ascii_letters as letters, digits, punctuation as punc

from flask import flash, make_response, redirect, render_template, request, url_for
from itsdangerous import BadPayload, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash

from web_shop.forms import MyChangePasswordForm, MyResetPasswordForm
from web_shop import app, db, token_serializer
from web_shop.database import User
from web_shop.emails import create_confirmation_token, create_message, send_message


@app.route("/confirm/<token>")
def confirm_email(token, token_age=None):
    """Confirm email after registration."""
    email = token_serializer.loads(token, salt=app.config["SECRET_KEY"])
    user = User.query.filter_by(email=email).first()
    if user:
        try:
            token_serializer.loads(token, salt=app.config["SECRET_KEY"], max_age=token_age if token_age else 60)
            user.confirmed_at = datetime.now()
            user.is_active = True
            db.session.commit()
            flash("Учётная запись подтверждена")
            return make_response(redirect(url_for("login")))
        except (BadPayload, BadSignature, SignatureExpired):
            if user.confirmed_at:
                return make_response(redirect(url_for("login")))
            db.session.delete(user)
            db.session.commit()
    flash("Ссылка недействительна. Пройдите регистрацию.")
    return make_response(redirect(url_for("register")))


@app.route("/retrieve", methods=["GET", "POST"])
def retrieve():
    """Password retrieve view."""
    if not request.args:
        form = MyResetPasswordForm()
        if form.is_submitted():
            if not form.email.data:
                flash("Адрес не указан")
                return make_response(render_template("retrieve_password.html", form=form))
            email = form.email.data.lower()
            user = User.query.filter_by(email=email).first()
            if user is None:
                flash("Пользователь не зарегистрирован")
            else:
                retrieve_password(user)
                flash("Ваш предыдущий пароль был сброшен. Проверьте свою почту.")
    else:
        form = MyChangePasswordForm()
        if not request.args.get("token"):
            flash("Ссылка недействительна")
            return make_response(render_template("retrieve_password.html", form=form))

        email, code, date = token_serializer.loads(request.args["token"], salt=app.config["SECRET_KEY"])

        if code != "retrieve_password":
            flash("Ссылка недействительна")
            return make_response(render_template("retrieve_password.html", form=form))

        if datetime.utcnow().timestamp() - date > 300:
            flash("Ссылка больше не действительна")
            return make_response(redirect(url_for("retrieve")))

        user = User.query.filter_by(email=email).first()

        if form.validate_on_submit():
            user.set_password(form.password.data)
            db.session.commit()
            flash("Пароль был успешно изменен.")
            return make_response(redirect(url_for("login")))

    return make_response(render_template("retrieve_password.html", title="Восстановление доступа", form=form))


def get_random_password():
    """Create random password."""
    result_str = "".join(i for _ in range(15) for i in random.choice(letters + digits + punc))
    return generate_password_hash(result_str)


def retrieve_password(user) -> None:
    """Change stored password by a random one and send a letter with a link for retrieve."""
    user.password = get_random_password()
    db.session.commit()
    token = create_confirmation_token((user.email, "retrieve_password", datetime.utcnow().timestamp()))
    link = url_for("retrieve", token=token, _external=True)
    message = create_message("Восстановление доступа на сайт WebShop", user.email)
    message.html = (
        f"Ваш предыдущий пароль был сброшен.<br>"
        f"Для создания нового пароля перейдите по <a href={link}>ссылке</a>.<br><br>"
        f"Ссылка действительна в течение 5 минут."
    )
    send_message(message)
