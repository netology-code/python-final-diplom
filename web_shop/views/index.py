"""Index view for login, logout and registration."""

from flask import make_response, render_template, request

from web_shop import app


@app.route("/")
def index():
    """Index view."""
    return make_response(render_template("base.html"))
