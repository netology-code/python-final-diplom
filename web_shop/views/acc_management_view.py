"""View for confirmation emails and tokens."""
import random
from datetime import datetime
from string import ascii_lowercase, ascii_uppercase, digits, punctuation

from flask import abort, flash, make_response, redirect, render_template, request, url_for
from itsdangerous import BadPayload, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash

from web_shop import app, db, token_serializer
from web_shop.database import User
from web_shop.emails import create_confirmation_token, create_message, send_message
from web_shop.forms import MyChangePasswordForm, MyResetPasswordForm


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
            return make_response(abort(404))

        try:
            email, code, date = token_serializer.loads(request.args["token"], salt=app.config["SECRET_KEY"])
        except (BadSignature, ValueError):
            return make_response(abort(404))

        if code != "retrieve_password" or datetime.utcnow().timestamp() - date > 300:
            flash("Ссылка недействительна")
            return make_response(redirect(url_for("retrieve")))

        user = User.query.filter_by(email=email).first()

        if form.validate_on_submit():
            user.set_password(form.password.data)
            db.session.commit()
            flash("Пароль был успешно изменен.")
            return make_response(redirect(url_for("login")))

    return make_response(render_template("retrieve_password.html", title="Восстановление доступа", form=form))


def create_random_password() -> str:
    """Create a random password."""
    random_password = []
    random_password.extend(i for _ in range(3) for i in random.choice(ascii_lowercase))
    random_password.extend(i for _ in range(3) for i in random.choice(ascii_uppercase))
    random_password.extend(i for _ in range(3) for i in random.choice(digits))
    random_password.extend(i for _ in range(3) for i in random.choice(punctuation))
    random.shuffle(random_password)
    return "".join(random_password)


def get_random_password_hash() -> str:
    """Create random password hash."""
    result_str = create_random_password()
    return generate_password_hash(result_str)


def retrieve_password(user) -> None:
    """Change stored password by a random one and send a letter with a link for retrieve."""
    user.password = get_random_password_hash()
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
