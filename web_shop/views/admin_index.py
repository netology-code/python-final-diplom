"""Admin-index view."""

from flask import make_response, redirect, url_for
from flask_admin import AdminIndexView
from flask_login import current_user


class MyAdminIndexView(AdminIndexView):
    """Overrides access to admin index page."""

    def is_accessible(self):
        """Lets user enter admin view on condition."""
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        """Redirects user to login view from admin view if user is anonymous."""
        return make_response(redirect(url_for("login", next="admin.index")))
