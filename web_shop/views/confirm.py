"""View for confirmation emails and tokens."""
from datetime import datetime

from flask import flash, make_response, redirect, url_for
from itsdangerous import BadPayload, BadSignature, SignatureExpired

from web_shop.database import User
from web_shop import app, db, token_serializer


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
