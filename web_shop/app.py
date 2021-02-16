"""Runs web_shop."""

from web_shop.config import app
import views


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
