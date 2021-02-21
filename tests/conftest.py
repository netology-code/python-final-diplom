"""Fixtures for tests."""

import os

import pytest
from flask_sqlalchemy import SQLAlchemy
from flask.testing import FlaskClient
from flask import Flask
from web_shop import app
from web_shop.config import basedir


@pytest.fixture(scope="session")
def database(test_app):
    """Database for tests."""
    from web_shop.database import models

    db = SQLAlchemy(app=test_app)
    db.create_all()
    yield db
    db.drop_all()


@pytest.fixture(scope="session")
def client():
    """Application for tests."""
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'tests', 'test.db')}"
    app.config.testing = True
    return app.test_client()
