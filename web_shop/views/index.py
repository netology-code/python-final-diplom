"""Index view.

In future shall redirect to ROOT_URL.
"""

from web_shop import app


@app.route("/")
def hello():
    """Index view."""
    app.logger.info("Going to index")
    return "Hello, World!"
