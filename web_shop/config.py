"""Web_shop configs."""

import os
from dotenv import load_dotenv

ROOT_URL = "/api/v1/"
basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()


class Config:
    """Application configurations."""

    SECRET_KEY = os.getenv("SECRET_KEY", "TEST_SECRET_KEY")
    JWT_SECRET_KEY = SECRET_KEY
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    FLASK_ADMIN_SWATCH = "cerulean"
    MAIL_SERVER = os.getenv("SMTP_SERVER")
    MAIL_NAME = os.getenv("SMTP_NAME")
    MAIL_USERNAME = os.getenv("SMTP_USERNAME")
    MAIL_PASSWORD = os.getenv("SMTP_PASSWORD")
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
