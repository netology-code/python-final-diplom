"""Test registration."""
import pytest
from bs4 import BeautifulSoup
from flask import Response, request, url_for

from web_shop.database import User

URL = "/register"


def test_get_register(client):
    """Test get-register."""
    with client:
        response = client.get(URL, content_type="html/text")
    assert response.status_code == 200
    response.text = BeautifulSoup(response.data, "html.parser").text
    assert response.text.lower().count("регистрация") == 3


class TestNormalRegister:
    """Tests for normal registration of a new user."""

    @pytest.mark.xfail(reason="No SMTP credentials for tests at GIT-actions")
    def test_post_register_normal(self, client, register_data):
        """Test normal registration of a new user. Follow redirection.

        Marked xfail for git actions.
        """
        assert not User.query.filter_by(email=register_data["email"]).first()
        with client:
            response: Response = client.post(URL, data=register_data, follow_redirects=True)
            assert response.status_code == 200
            assert "Регистрация прошла успешно!" in response.get_data(as_text=True)
            assert request.path == url_for("index")
            user = User.query.filter_by(email=register_data["email"]).first()
            assert user.user_type.name == register_data["user_type"]
            assert user.is_active is False
            assert user.confirmed_at is None

    @pytest.mark.xfail(reason="No SMTP credentials for tests at GIT-actions")
    def test_post_register_normal_no_redirect(self, client, register_data):
        """Test normal registration of a new user. No redirection.

        Marked xfail for git actions.
        """
        register_data["email"] = "email1@email.com"
        assert not User.query.filter_by(email=register_data["email"]).first()
        with client:
            response: Response = client.post(URL, data=register_data, follow_redirects=False)
            assert response.status_code == 302
            assert request.path == URL


def test_register_empty_form(client):
    """Empty form is submitted."""
    with client:
        response: Response = client.post(URL, follow_redirects=True)
        alerts = ["Имя не указано", "Фамилия не указана", "Адрес не указан", "Пароль не указан"]
        page = response.get_data(as_text=True)
        assert all(x in page for x in alerts)
        assert page.count("Пароль не указан") == 2
        assert request.path == URL


class TestOneFieldPassedFail:
    """Tests of registration failures when just one field is filled in."""

    def test_register_email(self, client, empty_register_data):
        """Just email is submitted. Other fields are empty."""
        empty_register_data["email"] = "email@email.com"
        with client:
            response: Response = client.post(URL, data=empty_register_data, follow_redirects=True)
            alerts = ["Имя не указано", "Фамилия не указана", "Пароль не указан"]
            page = response.get_data(as_text=True)
            assert all(x in page for x in alerts)
            assert "Адрес не указан" not in page
            assert page.count("Пароль не указан") == 2
            assert request.path == URL

    def test_register_first_name(self, client, empty_register_data):
        """Just first name is submitted. Other fields are empty."""
        empty_register_data["first_name"] = "test_name"
        with client:
            response: Response = client.post(URL, data=empty_register_data, follow_redirects=True)
            alerts = ["Фамилия не указана", "Адрес не указан", "Пароль не указан"]
            page = response.get_data(as_text=True)
            assert all(x in page for x in alerts)
            assert "Имя не указано" not in page
            assert page.count("Пароль не указан") == 2
            assert request.path == URL

    def test_register_last_name(self, client, empty_register_data):
        """Just last name is submitted. Other fields are empty."""
        empty_register_data["last_name"] = "test_surname"
        with client:
            response: Response = client.post(URL, data=empty_register_data, follow_redirects=True)
            alerts = ["Имя не указано", "Адрес не указан", "Пароль не указан"]
            page = response.get_data(as_text=True)
            assert all(x in page for x in alerts)
            assert "Фамилия не указана" not in page
            assert page.count("Пароль не указан") == 2
            assert request.path == URL

    def test_register_password(self, client, empty_register_data):
        """Just password is submitted. Other fields are empty."""
        empty_register_data["password"] = "testpass"
        with client:
            response: Response = client.post(URL, data=empty_register_data, follow_redirects=True)
            alerts = ["Имя не указано", "Фамилия не указана", "Адрес не указан"]
            page = response.get_data(as_text=True)
            assert all(x in page for x in alerts)
            assert page.count("Пароль не указан") == 1
            assert request.path == URL

    def test_register_password_confirm(self, client, empty_register_data):
        """Just password_confirm is submitted. Other fields are empty."""
        empty_register_data["password_confirm"] = "testpass"
        with client:
            response: Response = client.post(URL, data=empty_register_data, follow_redirects=True)
            alerts = ["Имя не указано", "Фамилия не указана", "Адрес не указан"]
            page = response.get_data(as_text=True)
            assert all(x in page for x in alerts)
            assert page.count("Пароль не указан") == 1
            assert request.path == URL

    def test_register_user_type(self, client, empty_register_data):
        """Just user_type is submitted. Other fields are empty."""
        empty_register_data["user_type"] = "shop"
        with client:
            response: Response = client.post(URL, data=empty_register_data, follow_redirects=True)
            alerts = ["Имя не указано", "Фамилия не указана", "Адрес не указан", "Пароль не указан"]
            page = response.get_data(as_text=True)
            assert all(x in page for x in alerts)
            assert request.path == URL


class TestOneFieldEmptyFail:
    """Tests of registration failures when just one field is filled in."""

    def test_register_empty_email(self, client, register_data):
        """Email is empty. Other fields are filled in."""
        register_data["email"] = ""
        with client:
            response: Response = client.post(URL, data=register_data, follow_redirects=True)
            alerts = ["Имя не указано", "Фамилия не указана", "Пароль не указан"]
            page = response.get_data(as_text=True)
            assert all(x not in page for x in alerts)
            assert "Адрес не указан" in page
            assert request.path == URL

    def test_register_empty_first_name(self, client, register_data):
        """First name is empty. Other fields are filled in."""
        register_data["first_name"] = ""
        with client:
            response: Response = client.post(URL, data=register_data, follow_redirects=True)
            alerts = ["Фамилия не указана", "Адрес не указан", "Пароль не указан"]
            page = response.get_data(as_text=True)
            assert all(x not in page for x in alerts)
            assert "Имя не указано" in page
            assert request.path == URL

    def test_register_empty_last_name(self, client, register_data):
        """Last name is empty. Other fields are filled in."""
        register_data["last_name"] = ""
        with client:
            response: Response = client.post(URL, data=register_data, follow_redirects=True)
            alerts = ["Имя не указано", "Адрес не указан", "Пароль не указан"]
            page = response.get_data(as_text=True)
            assert all(x not in page for x in alerts)
            assert "Фамилия не указана" in page
            assert request.path == URL

    def test_register_empty_password(self, client, register_data):
        """Password is empty. Other fields are filled in."""
        register_data["password"] = ""
        with client:
            response: Response = client.post(URL, data=register_data, follow_redirects=True)
            alerts = ["Имя не указано", "Фамилия не указана", "Адрес не указан"]
            page = response.get_data(as_text=True)
            assert all(x not in page for x in alerts)
            assert page.count("Пароль не указан") == 1
            assert request.path == URL

    def test_register_empty_password_confirm(self, client, register_data):
        """Password_confirm is empty. Other fields are filled in."""
        register_data["password_confirm"] = ""
        with client:
            response: Response = client.post(URL, data=register_data, follow_redirects=True)
            alerts = ["Имя не указано", "Фамилия не указана", "Адрес не указан"]
            page = response.get_data(as_text=True)
            assert all(x not in page for x in alerts)
            assert page.count("Пароль не указан") == 1
            assert request.path == URL

    def test_register_empty_user_type(self, client, register_data):
        """User_type is empty. Other fields are filled in."""
        register_data["user_type"] = ""
        with client:
            response: Response = client.post(URL, data=register_data, follow_redirects=True)
            alerts = ["Имя не указано", "Фамилия не указана", "Адрес не указан", "Пароль не указан"]
            page = response.get_data(as_text=True)
            assert all(x not in page for x in alerts)
            assert request.path == URL


class TestMistakesFail:
    """Test of registration fails caused by mistakes on submit."""

    @pytest.mark.parametrize(
        "string",
        [
            "a",
            "1",
            "mama",
            "@",
            ",",
            "mama@",
            "папa@a.c",
            "sud@a.com",
            "sud@ar.c",
            "sudo@a.com",
            "sudo@ar.c",
            "sudo@ar.compa",
            "supermario[2021]@gmail.com",
            "supermario@gmail,com",
            "supеrmаriо@gmаil.com",  # russian vowels
            "supermario+dendy@gmail.com",
        ],
    )
    def test_register_wrong_email(self, string, client, register_data):
        """Random string passed as email is not validated as email."""
        with client:
            register_data["email"] = string
            response: Response = client.post(URL, data=register_data, follow_redirects=True)
            assert "Введите адрес электронной почты" in response.get_data(as_text=True)


if __name__ == "__main__":
    pytest.main()
