"""Web_shop configs."""

import os
from dotenv import load_dotenv

ROOT_URL = "/api/v1/"
basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()


class Config:
    """Application configurations."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
