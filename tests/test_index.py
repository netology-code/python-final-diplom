"""Test app initiation."""
# from unittest.mock import patch
#
# from flask import Response
# from selenium import webdriver
# from selenium.webdriver import ActionChains
# from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pytest


def test_get_index_on_start(tester):
    """Test get-index.

    :return assertion
    """
    response = tester.get("/", content_type="html/text")
    assert response.status_code == 200
    response.text = BeautifulSoup(response.data, "html.parser").text
    assert "Добро пожаловать в магазин WebShop" in response.text


def test_get_register(tester):
    """Test get-register.

    :return assertion
    """
    response = tester.get("/register", content_type="html/text")
    assert response.status_code == 200
    response.text = BeautifulSoup(response.data, "html.parser").text
    assert response.text.lower().count("регистрация") == 3


def test_get_login(tester):
    """Test get-login.

    :return assertion
    """
    response = tester.get("/login", content_type="html/text")
    response.text = BeautifulSoup(response.data, "html.parser").text
    assert response.text.lower().count("вход") == 2


#
# @pytest.mark.parametrize("username, password", [
#     ("serge.rybakov@gmail.com", "123"),
#     # ("erge.rybakov@gmail.com", "123")
# ])
# def test_login_post_form(username, password, tester):
#     with tester:
#         a1: Response = tester.get('/login')
#         session1 = a1.headers['Set-Cookie'].split('session=')[-1].split(';')[0]
#
#         b: Response = tester.post('/login',
#                                          data=dict(email=username,
#                                                    password=password,
#                                                    submit=True
#                                                    ),
#                                follow_redirects=True
#                                         )
#         sessionb = b.headers['Set-Cookie'].split('session=')[-1].split(';')[0]
#
#         a2: Response = tester.get('/login')
#         session2 = a2.headers['Set-Cookie'].split('session=')[-1].split(';')[0]
#         a3: Response = tester.get('/login')
#         session3 = a3.headers['Set-Cookie'].split('session=')[-1].split(';')[0]
#
#         assert session3 == sessionb


# print(response.data.decode())
# print(111, response
# response.text = BeautifulSoup(response.data, "html.parser").text
# assert response.text == "a"


# @pytest.mark.parametrize(
#     ("first_name", "last_name", "email", "password", "password_confirm", "expected"),
#     [
#         ("test_name", "test_surname", "email@email.com", "password", "password", True),
#         (None, "test_surname", "email@email.com", "password", "password", False),
#     ],
# )
# def test_post_register(first_name, last_name, email, password, password_confirm, expected, tester, database):
#     with patch("web_shop.db", side_effect=database):
#         data = {
#             "first_name": first_name,
#             "last_name": last_name,
#             "email": email,
#             "password": password,
#             "password_confirm": password_confirm,
#             "form": "",
#         }
#         response = tester.post("/register", data=data, content_type="html/text", follow_redirects=True)
#         assert response.status_code == 200
#         response.text = BeautifulSoup(response.data, "html.parser").text
#         assert "Добро пожаловать в магазин WebShop" in response.text


if __name__ == "__main__":
    pytest.main()
