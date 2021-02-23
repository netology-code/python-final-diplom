"""Fixtures for tests."""

import os
from datetime import datetime

import pytest

from web_shop.database import User
from web_shop import app, db


@pytest.fixture(scope="session")
def client(test_app):
    """Test client."""
    return test_app.test_client()


@pytest.fixture(scope="session", autouse=True)
def database(test_app):
    """Database for tests."""
    from web_shop.database import models

    db.create_all()
    admin_buyer = User(email="admin_buyer@test.email", first_name="Admin", last_name="Buyer")
    admin_buyer.set_password("testpass1")
    admin_buyer.user_type = "buyer"
    admin_buyer.is_admin = True
    admin_buyer.confirmed_at = datetime.now()

    admin_shop = User(email="admin_shop@test.email", first_name="Admin", last_name="Shop")
    admin_shop.set_password("testpass2")
    admin_shop.user_type = "shop"
    admin_shop.is_admin = True
    admin_buyer.confirmed_at = datetime.now()

    non_admin_buyer = User(email="non_admin_buyer@test.email", first_name="NonAdmin", last_name="Buyer")
    non_admin_buyer.set_password("testpass3")
    non_admin_buyer.user_type = "buyer"
    admin_buyer.confirmed_at = datetime.now()

    non_admin_shop = User(email="non_admin_shop@test.email", first_name="NonAdmin", last_name="Shop")
    non_admin_shop.set_password("testpass4")
    non_admin_shop.user_type = "shop"
    admin_buyer.confirmed_at = datetime.now()

    for user in [admin_buyer, admin_shop, non_admin_shop, non_admin_buyer]:
        db.session.add(user)
        db.session.commit()
    yield db
    db.drop_all()


@pytest.fixture(scope="session")
def test_app():
    """Application modifications for tests."""
    DB_URI = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.db')}"
    app.config["SECRET_KEY"] = "TEST_SECRET_KEY"
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
    # app.config["SQLALCHEMY_ECHO"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config.testing = True
    return app
