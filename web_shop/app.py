"""Runs web_shop."""

from web_shop import app, db
from web_shop.database import User


@app.shell_context_processor
def make_shell_context():
    """Create Flask Shell access."""
    return {"db": db, "User": User}


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
