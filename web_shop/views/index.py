"""Index view.

In future shall redirect to ROOT_URL.
"""

from web_shop.config import app


@app.route("/")
def hello():
    """Index view."""
    return "Hello, World!"
