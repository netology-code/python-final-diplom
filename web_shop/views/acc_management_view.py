"""View for confirmation emails and tokens."""
import random
from datetime import datetime
from string import ascii_lowercase, ascii_uppercase, digits, punctuation

from flask import (
    abort,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from itsdangerous import BadPayload, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash

from web_shop import app, db, token_serializer
from web_shop.database import Order, OrderStateChoices, User
from web_shop.emails import (
    create_confirmation_token,
    create_message,
    send_message,
)
from web_shop.forms import (
    MyEmailChangeForm,
    MyNameChangeForm,
    MyPasswordChangeForm,
    MyResetPasswordForm,
)
from web_shop.validators import MyEmailValidator
from web_shop.views.orders_view import confirm_order, send_messages_on_order_confirmation


@app.route("/account")
@login_required
def account():
    """View for account data."""
    return make_response(render_template("account.html"))


@app.route("/account/edit", methods=["GET", "POST"])
@login_required
def account_edit():
    """View for edit account data."""
    if "status" in request.args:
        user = User.query.filter_by(email=current_user.email).first()
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        db.session.commit()
        return make_response(redirect(url_for("account")))

    if "name" in request.args:
        form = MyNameChangeForm()
    elif "password" in request.args:
        form = MyPasswordChangeForm()
    elif "email" in request.args:
        form = MyEmailChangeForm()
    else:
        return make_response(abort(404))

    if form.cancel.data:
        return make_response(redirect(url_for("account")))

    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if isinstance(form, MyEmailChangeForm):
            if form.email.data:
                user.email = form.email.data.lower()
        elif isinstance(form, MyNameChangeForm):
            if form.first_name.data:
                user.first_name = form.first_name.data
            if form.last_name.data:
                user.last_name = form.last_name.data
        elif isinstance(form, MyPasswordChangeForm):
            if form.password.data:
                user.password = user.set_password(form.password.data)
        db.session.commit()
        return make_response(redirect(url_for("account")))

    return make_response(render_template("account_edit.html", form=form))


@app.route("/confirm/<token>")
def confirm(token, token_age=None):
    """Confirm email after registration."""
    data = token_serializer.loads(token, salt=app.config["SECRET_KEY"])
    if isinstance(data, str) and MyEmailValidator(data):
        email = data
        user = User.query.filter_by(email=email).first()
        if user:
            try:
                token_serializer.loads(
                    token,
                    salt=app.config["SECRET_KEY"],
                    max_age=token_age if token_age else 60,
                )
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

    if isinstance(data, (tuple, list)):
        email, order_id, token_age = data
        order: Order = Order.query.get(order_id)

        if not order:
            flash("Такого заказа не существует.")
            return make_response(redirect(url_for("list_orders")))

        if not current_user.email == email:
            flash("Данная ссылка предназначена для другого пользователя.")
            return make_response(redirect(url_for("list_orders")))

        if order.status == OrderStateChoices.canceled:
            flash("Данный заказ был отменён.")
            return make_response(redirect(url_for("list_orders")))

        if not order.status == OrderStateChoices.awaiting:
            flash("Данный заказ уже был подтверждён.")
            return make_response(redirect(url_for("list_orders")))

        try:
            token_serializer.loads(
                token,
                salt=app.config["SECRET_KEY"],
                max_age=token_age if token_age else 60,
            )
            items, total_sum = confirm_order(order)
            send_messages_on_order_confirmation(order, items, total_sum)
            return make_response(redirect(url_for("list_orders") + "?type=confirmed"))

        except (BadPayload, BadSignature, SignatureExpired):
            order: Order = Order.query.get(order_id)
            order.status = OrderStateChoices.canceled.name
            order._last_change = datetime.utcnow()
            db.session.commit()
            flash("Ссылка недействительна. Заказ отменён.")
            return make_response(redirect(url_for("list_orders")))


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
                return make_response(redirect(url_for("index")))
    else:
        form = MyPasswordChangeForm()
        if not request.args.get("token"):
            flash("Ссылка недействительна")
            return make_response(abort(404))

        try:
            email, code, date = token_serializer.loads(
                request.args["token"], salt=app.config["SECRET_KEY"]
            )
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

    return make_response(
        render_template(
            "retrieve_password.html", title="Восстановление доступа", form=form
        )
    )


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
    token = create_confirmation_token(
        (user.email, "retrieve_password", datetime.utcnow().timestamp())
    )
    link = url_for("retrieve", token=token, _external=True)
    message = create_message("Восстановление доступа на сайт WebShop", user.email)
    message.html = (
        f"Ваш предыдущий пароль был сброшен.<br>"
        f"Для создания нового пароля перейдите по <a href={link}>ссылке</a>.<br><br>"
        f"Ссылка действительна в течение 5 минут."
    )
    send_message(message)
