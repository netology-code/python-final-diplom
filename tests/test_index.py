"""Test app initiation."""
import pytest

# from selenium import webdriver
# from selenium.webdriver import ActionChains
# from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# from unittest.mock import patch
#
from flask import Response, request
from flask_login import current_user


# @pytest.mark.xfail
def test_get_index_on_start(client):
    """Test get-index.

    :return assertion
    """
    response = client.get("/", content_type="html/text")
    assert response.status_code == 200
    response.text = BeautifulSoup(response.data, "html.parser").text
    assert "Добро пожаловать в магазин WebShop" in response.text


# @pytest.mark.xfail
def test_get_register(client):
    """Test get-register.

    :return assertion
    """
    with client:
        response = client.get("/register", content_type="html/text")
    assert response.status_code == 200
    response.text = BeautifulSoup(response.data, "html.parser").text
    assert response.text.lower().count("регистрация") == 3


# @pytest.mark.xfail
def test_get_login(client):
    """Test get-login.

    :return assertion
    """
    with client:
        response = client.get("/login", content_type="html/text")
    response.text = BeautifulSoup(response.data, "html.parser").text
    assert response.text.lower().count("вход") == 2


@pytest.mark.parametrize(
    ("username", "pwd", "is_admin", "user_type"),
    [
        ("admin_buyer@test.email", "testpass1", True, "buyer"),
        ("admin_shop@test.email", "testpass2", True, "shop"),
        ("non_admin_buyer@test.email", "testpass3", False, "buyer"),
        ("non_admin_shop@test.email", "testpass4", False, "shop"),
    ],
)
def test_login_post_form_existing_users_no_redirection(username, pwd, is_admin, user_type, client):
    """Test logging in existing users. Catch redirect code with no redirection."""
    with client:
        response: Response = client.post(
            "/login", data=dict(email=username, password=pwd, remember_me=False), follow_redirects=False
        )
        assert response.status_code == 302
        assert current_user.is_admin == is_admin
        assert current_user.user_type.name == user_type
        assert "Админка" not in response.get_data(as_text=True)
        client.get("/logout")


@pytest.mark.parametrize(
    ("username", "pwd", "is_admin", "user_type"),
    [
        ("admin_buyer@test.email", "testpass1", True, "buyer"),
        ("admin_shop@test.email", "testpass2", True, "shop"),
        ("non_admin_buyer@test.email", "testpass3", False, "buyer"),
        ("non_admin_shop@test.email", "testpass4", False, "shop"),
    ],
)
def test_login_post_form_existing_users_redirection(username, pwd, is_admin, user_type, client):
    """Test logging in existing users. Catch redirection."""
    with client:
        response: Response = client.post(
            "/login", data=dict(email=username, password=pwd, remember_me=False), follow_redirects=True
        )
        assert response.status_code == 200
        assert current_user.user_type.name == user_type
        assert ("Админка" in response.get_data(as_text=True)) == is_admin
        client.get("/logout")


# @pytest.mark.parametrize(
#     ("first_name", "last_name", "email", "password", "password_confirm", "expected"),
#     [
#         ("test_name", "test_surname", "email@email.com", "password", "password", True),
#         (None, "test_surname", "email@email.com", "password", "password", False),
#     ],
# )
# def test_post_register(first_name, last_name, email, password, password_confirm, expected, client, database):
#     with patch("web_shop.db", side_effect=database):
#         data = {
#             "first_name": first_name,
#             "last_name": last_name,
#             "email": email,
#             "password": password,
#             "password_confirm": password_confirm,
#             "form": "",
#         }
#         response = client.post("/register", data=data, content_type="html/text", follow_redirects=True)
#         assert response.status_code == 200
#         response.text = BeautifulSoup(response.data, "html.parser").text
#         assert "Добро пожаловать в магазин WebShop" in response.text


if __name__ == "__main__":
    pytest.main()
