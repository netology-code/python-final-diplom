"""Web_shop inits."""

import os

from celery import Celery
from flask import Flask
from flask_admin import Admin
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer

from web_shop.config import Config, basedir

# Init app
app = Flask(__name__)
app.config.from_object(Config)

# Init db
db = SQLAlchemy(app)

# Init admin
jwt = JWTManager(app)

# Init mail
mail = Mail(app)
token_serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# Initialize Celery
celery = Celery(
    app.name,
    broker=app.config["CELERY_BROKER_URL"],
    backend=app.config["CELERY_RESULT_BACKEND"],
    include=app.config["CELERY_INCLUDE"],
)
celery.conf.update(app.config)


# Init login
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Init migrations
directory = os.path.join(basedir, "database", "migrations")
migrate = Migrate(app, db, directory=directory)
from web_shop.database import models, UserAdmin, ShopAdmin

# Init admin
from web_shop.views import MyAdminIndexView


admin = Admin(
    app, name="Admin", template_mode="bootstrap3", index_view=MyAdminIndexView()
)
admin.add_view(UserAdmin(models.User, db.session))
admin.add_view(ShopAdmin(models.Shop, db.session))
