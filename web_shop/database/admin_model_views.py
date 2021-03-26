"""Admin-model views."""

from flask_admin.contrib.sqla import ModelView

from web_shop.database import User
from web_shop.views import retrieve_password


class UserAdmin(ModelView):
    """User model view in admin panel."""

    column_list = (
        "id",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_admin",
        "confirmed_at",
        "user_type",
    )

    can_edit = True
    can_create = True
    can_delete = True

    def on_model_change(self, form, model, is_created):
        user = User.query.filter_by(email=model.email).first()
        if not is_created:
            if not user.password.startswith("pbkdf2:sha256:150000"):
                retrieve_password(user)
        # else:


class ShopAdmin(ModelView):
    """Shop model view in admin panel."""

    column_list = (
        "id",
        "title",
        "url",
        "filename",
        "file_upload_datetime",
        "user_id",
    )
    form_args = {
        "shop_manager": {
            "query_factory": lambda: User.query.filter_by(user_type="seller").order_by(
                "email"
            )
        }
    }
    can_edit = True
    can_create = True
    can_delete = True
