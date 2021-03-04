"""Fixtures for tests."""

import os
from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from web_shop import app, db
from web_shop.database import User


@pytest.fixture()
def client(test_app):
    """Test client."""
    return test_app.test_client()


@pytest.fixture(scope="module", autouse=True)
def database(test_app):
    """Database for tests."""
    from web_shop.database import models

    try:
        db.create_all()
        users = create_db_confirmed_users() + create_db_unconfirmed_users()
        db.session.bulk_save_objects(users)
        db.session.commit()
        yield db
    except IntegrityError:
        db.drop_all()
        users = create_db_confirmed_users() + create_db_unconfirmed_users()
        db.session.bulk_save_objects(users)
        db.session.commit()
        yield db
    finally:
        db.drop_all()


@pytest.fixture(scope="session")
def test_app():
    """Application modifications for tests."""
    TEST_DB_URI = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.db')}"
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = TEST_DB_URI
    # app.config["SQLALCHEMY_ECHO"] = True
    app_context = app.test_request_context()
    app_context.push()
    return app


@pytest.fixture()
def empty_register_data():
    """Empty data for register view."""
    return dict(email="", first_name="", last_name="", password="", password_confirm="", user_type="")


@pytest.fixture()
def login_admin():
    """Data for login view."""
    return dict(email="admin_buyer@test.mail", password="testpass1")


@pytest.fixture()
def login_non_admin():
    """Data for login view."""
    return dict(email="non_admin_buyer@test.mail", password="testpass3")


@pytest.fixture()
def register_data():
    """Data for register view."""
    return dict(
        first_name="test_name",
        last_name="test_surname",
        email="email@email.com",
        password="Password.1",
        password_confirm="Password.1",
        user_type="shop",
    )


def create_db_confirmed_users():
    """Users with confirmed email."""
    admin_buyer = User(email="admin_buyer@test.mail", first_name="Admin", last_name="Buyer")
    admin_buyer.set_password("testpass1")
    admin_buyer.user_type = "buyer"
    admin_buyer.is_admin = True
    admin_buyer.is_active = False
    admin_buyer.confirmed_at = datetime.now()

    admin_shop = User(email="admin_shop@test.mail", first_name="Admin", last_name="Shop")
    admin_shop.set_password("testpass2")
    admin_shop.user_type = "shop"
    admin_shop.is_admin = True
    admin_shop.is_active = True
    admin_shop.confirmed_at = datetime.now()

    non_admin_buyer = User(email="non_admin_buyer@test.mail", first_name="NonAdmin", last_name="Buyer")
    non_admin_buyer.set_password("testpass3")
    non_admin_buyer.user_type = "buyer"
    non_admin_buyer.is_active = True
    non_admin_buyer.confirmed_at = datetime.now()

    non_admin_shop = User(email="non_admin_shop@test.mail", first_name="NonAdmin", last_name="Shop")
    non_admin_shop.set_password("testpass4")
    non_admin_shop.user_type = "shop"
    non_admin_shop.is_active = True
    non_admin_shop.confirmed_at = datetime.now()

    return admin_buyer, admin_shop, non_admin_shop, non_admin_buyer


def create_db_unconfirmed_users():
    """Users with unconfirmed email."""
    admin_buyer_unc = User(email="admin_buyer_unc@test.mail", first_name="Admin_unc", last_name="Buyer_unc")
    admin_buyer_unc.set_password("testpass1")
    admin_buyer_unc.user_type = "buyer"
    admin_buyer_unc.is_admin = True

    admin_shop_unc = User(email="admin_shop_unc@test.mail", first_name="Admin_unc", last_name="Shop_unc")
    admin_shop_unc.set_password("testpass2")
    admin_shop_unc.user_type = "shop"
    admin_shop_unc.is_admin = True

    non_admin_buyer_unc = User(email="non_admin_buyer_unc@test.mail", first_name="NonAdmin_unc", last_name="Buyer_unc")
    non_admin_buyer_unc.set_password("testpass3")
    non_admin_buyer_unc.user_type = "buyer"

    non_admin_shop_unc = User(email="non_admin_shop_unc@test.mail", first_name="NonAdmin_unc", last_name="Shop_unc")
    non_admin_shop_unc.set_password("testpass4")
    non_admin_shop_unc.user_type = "shop"

    return admin_buyer_unc, admin_shop_unc, non_admin_shop_unc, non_admin_buyer_unc
