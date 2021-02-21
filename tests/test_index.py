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


def test_get_index_on_start(client):
    """Test get-index.

    :return assertion
    """
    response = client.get("/", content_type="html/text")
    assert response.status_code == 200
    response.text = BeautifulSoup(response.data, "html.parser").text
    assert "Добро пожаловать в магазин WebShop" in response.text


def test_get_register(client):
    """Test get-register.

    :return assertion
    """
    response = client.get("/register", content_type="html/text")
    assert response.status_code == 200
    response.text = BeautifulSoup(response.data, "html.parser").text
    assert response.text.lower().count("регистрация") == 3


def test_get_login(client):
    """Test get-login.

    :return assertion
    """
    response = client.get("/login", content_type="html/text")
    response.text = BeautifulSoup(response.data, "html.parser").text
    assert response.text.lower().count("вход") == 2


# @pytest.mark.parametrize(("username", "pwd"), [
#     ("serge.rybakov@gmail.com", "123"),
#     # ("erge.rybakov@gmail.com", "123")
# ])
# def test_login_post_form(username, pwd, client):
#     with client:
#         r: Response = client.post('/login',
#                                   data=dict(email=username, password=pwd),
#                                   follow_redirects=True
#                                   )
#
#         assert r.get_data(as_text=True) == 302
#
#
#         print(response.data.decode())
#         print(111, response
#         response.text = BeautifulSoup(response.data, "html.parser").text
#         assert response.text == "a"


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
