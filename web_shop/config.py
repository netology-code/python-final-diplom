"""Web_shop configs."""

import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()


class Config:
    """Application configurations."""

    # Admin
    FLASK_ADMIN_SWATCH = "cerulean"

    # Celery
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    CELERY_INCLUDE = []

    # Files
    ALLOWED_EXTENSIONS = {"yaml"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 megabytes - is a maximum file-size
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")

    # JSON
    JSON_AS_ASCII = False

    # Mail
    MAIL_NAME = os.getenv("SMTP_NAME")
    MAIL_PASSWORD = os.getenv("SMTP_PASSWORD")
    MAIL_PORT = 465
    MAIL_SERVER = os.getenv("SMTP_SERVER")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv("SMTP_USERNAME")

    # Secrets
    SECRET_KEY = os.getenv("SECRET_KEY", "TEST_SECRET_KEY")
    JWT_SECRET_KEY = SECRET_KEY

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
