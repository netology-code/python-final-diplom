"""Web_shop inits."""

import os

from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from web_shop.config import Config

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config.from_object(Config)

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

migrate = Migrate(app, db)
from web_shop.database import models
