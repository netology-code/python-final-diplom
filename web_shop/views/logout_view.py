"""Logout views."""

from flask import make_response, redirect, url_for
from flask_login import logout_user

from web_shop import app


@app.route("/logout")
def logout():
    """Logout user route handler."""
    logout_user()
    return make_response(redirect(url_for("index")))
