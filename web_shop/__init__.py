"""Web_shop inits."""

import os

from flask import Flask
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from web_shop.config import Config, basedir

# Init app
app = Flask(__name__)
app.config.from_object(Config)

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

# Init login
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Init migrations
directory = os.path.join(basedir, "database", "migrations")
migrate = Migrate(app, db, directory=directory)
from web_shop.database import models
