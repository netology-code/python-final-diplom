"""Fixtures for tests."""

import os

import pytest
from flask_sqlalchemy import SQLAlchemy
from flask.testing import FlaskClient
from web_shop import app


@pytest.fixture(scope="session")
def tester(test_app):
    """Client for tests."""
    return test_app.test_client()


@pytest.fixture(scope="session")
def database(test_app):
    """Database for tests."""
    db = SQLAlchemy(app=test_app)
    db.create_all()
    yield db
    db.drop_all()


@pytest.fixture(scope="session")
def test_app():
    """Application for tests."""
    app.config.testing = True
    app.config.SQLALCHEMY_DATABASE_URI = "sqlite:///test_db"
    app.config.SECRET_KEY = os.getenv("SECRET_KEY")
    app.config.JSON_AS_ASCII = False
    from web_shop import views

    return app
