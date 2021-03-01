"""Admin-model views."""

from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash

from web_shop.database import User
from web_shop.emails import create_confirmation_token, create_message, send_message


class UserAdmin(ModelView):
    """User model view in admin panel."""

    column_list = (
        "id",
        "email",
        "first_name",
        "last_name",
        "password",
        "is_active",
        "is_admin",
        "confirmed_at",
        "user_type",
    )
    column_exclude_list = "password"
    can_edit = True
    can_create = True
    can_delete = True
    can_export = True

    def on_model_change(self, form, model, is_created):
        raw_password = model.password
        model.password = generate_password_hash(model.password)
        user = User.query.filter_by(email=model.email).first()
        token = create_confirmation_token(user.email)
        message = create_message(model.email, token)
        if not user.confirmed_at:
            message.body += f"\n\nЛогин: {model.email}\nВаш пароль: {raw_password}"
        else:
            message.body = f"Ваш новый пароль: {raw_password}"
        send_message(message)
