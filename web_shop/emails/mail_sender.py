"""Email creating module."""

from flask import url_for
from flask_mail import Message

from web_shop import app, token_serializer


def create_confirmation_token(email):
    """Create confirmation token to be sent via email after registration."""
    return token_serializer.dumps(email, salt=app.config["SECRET_KEY"])


def create_message(email, token):
    """Create a confirmation message to be sent via email after registration."""
    msg = Message("Подтверждение регистрации", recipients=[email], sender=app.config["MAIL_NAME"])
    link = url_for("confirm_email", token=token, _external=True)
    msg.body = f"Для подтверждения учётной записи на WebShop перейдите по ссылке: {link}"
    return msg
