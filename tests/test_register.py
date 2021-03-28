"""Test registration."""
from unittest.mock import patch

import pytest
from flask import Response, request, url_for
from flask_login import current_user

from web_shop.database import User

BASE_URL = "/register"


class TestCommonRegister:
    """Common tests."""

    def test_get_register(self, client):
        """Test get-register."""
        with client:
            response: Response = client.get(BASE_URL, content_type="html/text")
            assert response.status_code == 200
            assert response.get_data(as_text=True).lower().count("регистрация") == 2

    def test_get_register_logged_in(self, client, login_admin):
        """Test get-register by a logged-in user."""
        with client:
            client.post("/login", data=login_admin, follow_redirects=True)
            assert current_user.is_authenticated
            response: Response = client.get(
                BASE_URL, content_type="html/text", follow_redirects=True
            )
            assert "Выйти" in response.get_data(as_text=True)
            assert request.path == url_for("index")
            client.get("/logout", content_type="html/text")
            assert current_user.is_anonymous

    def test_register_empty_form(self, client):
        """Empty form is submitted."""
        with client:
            response: Response = client.post(BASE_URL, follow_redirects=True)
            alerts = [
                "Имя не указано",
                "Фамилия не указана",
                "Адрес не указан",
                "Пароль не указан",
            ]
            page = response.get_data(as_text=True)
            assert all(x in page for x in alerts)
            assert page.count("Пароль не указан") == 2
            assert request.path == BASE_URL

    def test_cancel(self, client):
        with client:
            client.get(BASE_URL)
            assert request.path == BASE_URL
            client.post(BASE_URL, data={"cancel": "cancel"}, follow_redirects=True)
            assert request.path == url_for("index")


class TestNormalRegister:
    """Tests for normal registration of a new user."""

    def test_post_register_normal(self, client, register_data):
        """Test normal registration of a new user. Follow redirection."""
        assert not User.query.filter_by(email=register_data["email"]).first()
        with client:
            with patch("web_shop.views.register_view.send_message"):
                response: Response = client.post(
                    BASE_URL, data=register_data, follow_redirects=True
                )
                assert response.status_code == 200
                assert "Регистрация прошла успешно!" in response.get_data(as_text=True)
                assert request.path == url_for("index")
                user = User.query.filter_by(email=register_data["email"]).first()
                assert user.user_type.name == register_data["user_type"]
                assert user.is_active is False
                assert user.confirmed_at is None

    def test_post_register_normal_no_redirect(self, client, register_data):
        """Test normal registration of a new user. No redirection."""
        register_data["email"] = "email1@email.com"
        assert not User.query.filter_by(email=register_data["email"]).first()
        with client:
            with patch("web_shop.views.register_view.send_message"):
                response: Response = client.post(
                    BASE_URL, data=register_data, follow_redirects=False
                )
                assert response.status_code == 302
                assert request.path == BASE_URL


class TestOneFieldPassedFail:
    """Tests of registration failures when just one field is filled in."""

    def test_register_email(self, client, empty_register_data):
        """Just email is submitted. Other fields are empty."""
        empty_register_data["email"] = "email@email.com"
        with client:
            response: Response = client.post(
                BASE_URL, data=empty_register_data, follow_redirects=True
            )
            alerts = [
                "Имя не указано",
                "Фамилия не указана",
                "Пароль не указан",
            ]
            page = response.get_data(as_text=True)
            assert all(x in page for x in alerts)
            assert "Адрес не указан" not in page
            assert page.count("Пароль не указан") == 2
            assert request.path == BASE_URL

    def test_register_first_name(self, client, empty_register_data):
        """Just first name is submitted. Other fields are empty."""
        empty_register_data["first_name"] = "test_name"
        with client:
            response: Response = client.post(
                BASE_URL, data=empty_register_data, follow_redirects=True
            )
            alerts = [
                "Фамилия не указана",
                "Адрес не указан",
                "Пароль не указан",
            ]
            page = response.get_data(as_text=True)
            assert all(x in page for x in alerts)
            assert "Имя не указано" not in page
            assert page.count("Пароль не указан") == 2
            assert request.path == BASE_URL

    def test_register_last_name(self, client, empty_register_data):
        """Just last name is submitted. Other fields are empty."""
        empty_register_data["last_name"] = "test_surname"
        with client:
            response: Response = client.post(
                BASE_URL, data=empty_register_data, follow_redirects=True
            )
            alerts = ["Имя не указано", "Адрес не указан", "Пароль не указан"]
            page = response.get_data(as_text=True)
            assert all(x in page for x in alerts)
            assert "Фамилия не указана" not in page
            assert page.count("Пароль не указан") == 2
            assert request.path == BASE_URL

    def test_register_password(self, client, empty_register_data):
        """Just password is submitted. Other fields are empty."""
        empty_register_data["password"] = "testpass"
        with client:
            response: Response = client.post(
                BASE_URL, data=empty_register_data, follow_redirects=True
            )
            alerts = ["Имя не указано", "Фамилия не указана", "Адрес не указан"]
            page = response.get_data(as_text=True)
            assert all(x in page for x in alerts)
            assert page.count("Пароль не указан") == 1
            assert request.path == BASE_URL

    def test_register_password_confirm(self, client, empty_register_data):
        """Just password_confirm is submitted. Other fields are empty."""
        empty_register_data["password_confirm"] = "testpass"
        with client:
            response: Response = client.post(
                BASE_URL, data=empty_register_data, follow_redirects=True
            )
            alerts = ["Имя не указано", "Фамилия не указана", "Адрес не указан"]
            page = response.get_data(as_text=True)
            assert all(x in page for x in alerts)
            assert page.count("Пароль не указан") == 1
            assert request.path == BASE_URL

    def test_register_user_type(self, client, empty_register_data):
        """Just user_type is submitted. Other fields are empty."""
        empty_register_data["user_type"] = "seller"
        with client:
            response: Response = client.post(
                BASE_URL, data=empty_register_data, follow_redirects=True
            )
            alerts = [
                "Имя не указано",
                "Фамилия не указана",
                "Адрес не указан",
                "Пароль не указан",
            ]
            page = response.get_data(as_text=True)
            assert all(x in page for x in alerts)
            assert request.path == BASE_URL


class TestOneFieldEmptyFail:
    """Tests of registration failures when just one field is filled in."""

    def test_register_empty_email(self, client, register_data):
        """Email is empty. Other fields are filled in."""
        register_data["email"] = ""
        with client:
            response: Response = client.post(
                BASE_URL, data=register_data, follow_redirects=True
            )
            alerts = [
                "Имя не указано",
                "Фамилия не указана",
                "Пароль не указан",
            ]
            page = response.get_data(as_text=True)
            assert all(x not in page for x in alerts)
            assert "Адрес не указан" in page
            assert request.path == BASE_URL

    def test_register_empty_first_name(self, client, register_data):
        """First name is empty. Other fields are filled in."""
        register_data["first_name"] = ""
        with client:
            response: Response = client.post(
                BASE_URL, data=register_data, follow_redirects=True
            )
            alerts = [
                "Фамилия не указана",
                "Адрес не указан",
                "Пароль не указан",
            ]
            page = response.get_data(as_text=True)
            assert all(x not in page for x in alerts)
            assert "Имя не указано" in page
            assert request.path == BASE_URL

    def test_register_empty_last_name(self, client, register_data):
        """Last name is empty. Other fields are filled in."""
        register_data["last_name"] = ""
        with client:
            response: Response = client.post(
                BASE_URL, data=register_data, follow_redirects=True
            )
            alerts = ["Имя не указано", "Адрес не указан", "Пароль не указан"]
            page = response.get_data(as_text=True)
            assert all(x not in page for x in alerts)
            assert "Фамилия не указана" in page
            assert request.path == BASE_URL

    def test_register_empty_password(self, client, register_data):
        """Password is empty. Other fields are filled in."""
        register_data["password"] = ""
        with client:
            response: Response = client.post(
                BASE_URL, data=register_data, follow_redirects=True
            )
            alerts = ["Имя не указано", "Фамилия не указана", "Адрес не указан"]
            page = response.get_data(as_text=True)
            assert all(x not in page for x in alerts)
            assert page.count("Пароль не указан") == 1
            assert request.path == BASE_URL

    def test_register_empty_password_confirm(self, client, register_data):
        """Password_confirm is empty. Other fields are filled in."""
        register_data["password_confirm"] = ""
        with client:
            response: Response = client.post(
                BASE_URL, data=register_data, follow_redirects=True
            )
            alerts = ["Имя не указано", "Фамилия не указана", "Адрес не указан"]
            page = response.get_data(as_text=True)
            assert all(x not in page for x in alerts)
            assert page.count("Пароль не указан") == 1
            assert request.path == BASE_URL

    def test_register_empty_user_type(self, client, register_data):
        """User_type is empty. Other fields are filled in."""
        register_data["user_type"] = ""
        with client:
            response: Response = client.post(
                BASE_URL, data=register_data, follow_redirects=True
            )
            alerts = [
                "Имя не указано",
                "Фамилия не указана",
                "Адрес не указан",
                "Пароль не указан",
            ]
            page = response.get_data(as_text=True)
            assert all(x not in page for x in alerts)
            assert request.path == BASE_URL


class TestMistakesFail:
    """Test of registration fails caused by mistakes on submit."""

    @pytest.mark.parametrize(
        ("string", "message"),
        [
            ("", "Адрес не указан"),
            (" ", "Адрес не указан"),
            ("  ", "Адрес не указан"),
            ("              ", "Адрес не указан"),
            ("a", "Длина имени адреса до символа"),
            ("1", "Длина имени адреса до символа"),
            ("@", "Длина имени адреса до символа"),
            ("sud@a.com", "Длина имени адреса до символа"),
            ("sud@ar.c", "Длина имени адреса до символа"),
            ("mama", "В адресе почты должен быть один символ"),
            ("12345", "В адресе почты должен быть один символ"),
            ("mama@@", "В адресе почты может быть только один символ"),
            ("super@mario@gmail.com", "В адресе почты может быть только один символ",),
            ("mama@", "Длина доменного имени должна быть не менее 2 символов"),
            ("sudo@a.com", "Длина доменного имени должна быть не менее 2 символов",),
            (
                "sudo@ar.c",
                "Длина доменной зоны должна быть не менее 2 и не более 4 символов",
            ),
            (
                "sudo@ar.compa",
                "Длина доменной зоны должна быть не менее 2 и не более 4 символов",
            ),
            (
                "supеrmаriо@gmаil.com",
                "Буквы могут быть только латинскими",
            ),  # russian vowels
            ("папa@a.c", "Буквы могут быть только латинскими",),  # russian letters
            (
                "supermario[2021]@gmail.com",
                "Недопустимые знаки препинания в адресе почты",
            ),
            (",", "Недопустимые знаки препинания в адресе почты"),
            ("supermario@gmail,com", "Недопустимые знаки препинания в адресе почты",),
            (
                "supermario+dendy@gmail.com",
                "Недопустимые знаки препинания в адресе почты",
            ),
            ("         @", "Недопустимые знаки препинания в адресе почты"),
            (
                "         @          .    ",
                "Недопустимые знаки препинания в адресе почты",
            ),
        ],
    )
    def test_register_wrong_email(self, string, client, register_data, message):
        """String passed to email field is not valid."""
        with client:
            register_data["email"] = string
            response: Response = client.post(
                BASE_URL, data=register_data, follow_redirects=True
            )
            assert message in response.get_data(as_text=True)

    @pytest.mark.parametrize(
        "string",
        [
            "admin_buyer_unc@test.mail",
            "admin_shop_unc@test.mail",
            "non_admin_buyer_unc@test.mail",
            "non_admin_shop_unc@test.mail",
        ],
    )
    def test_register_same_email(self, string, client, register_data):
        """Passing an email that was already registered and stored in database."""
        with client:
            register_data["email"] = string
            response: Response = client.post(
                BASE_URL, data=register_data, follow_redirects=True
            )
            assert "Данный адрес электронной почты уже используется" in response.get_data(
                as_text=True
            )
            assert request.path == BASE_URL

    @pytest.mark.parametrize(
        ("password", "password_confirm"),
        [
            ("testpass", ""),
            ("testpass", " "),
            ("testpass", "1"),
            ("testpass", "12345678"),
            ("testpass", "a"),
            ("testpass", "Testpass"),
            ("testpass", "TESTPASS"),
            ("testpass", "TeStPaSs"),
            ("Testpass", "TeStPaSs"),
            ("TESTPASS", "testpass"),
            ("testpass", "testpas"),
            ("testpass", "_testpass"),
            ("testpass", "estpass"),
            ("", "testpass"),
            (" ", "testpass"),
            ("testpass", "tеstpаss"),  # russian vowels
        ],
    )
    def test_register_password_confirmation_mistake(
        self, password, password_confirm, client, register_data
    ):
        """Passing different strings in password and password_confirm fields."""
        with client:
            register_data["password"] = password
            register_data["password_confirm"] = password_confirm
            response: Response = client.post(
                BASE_URL, data=register_data, follow_redirects=True
            )
            assert "Пароли не совпадают" in response.get_data(as_text=True)
            assert response.get_data(as_text=True).count("Пароли не совпадают") in range(
                1, 3
            )
            assert request.path == BASE_URL

    @pytest.mark.parametrize(
        ("string", "message"),
        [
            ("", "Пароль не указан"),
            (" ", "Пароль не указан"),
            ("  ", "Пароль не указан"),
            ("              ", "Пароль не указан"),
            ("a", "Длина пароля должна быть не менее 8 и не более 14 символов"),
            (
                "а",
                "Длина пароля должна быть не менее 8 и не более 14 символов",
            ),  # russian vowels
            ("q1!W2@e", "Длина пароля должна быть не менее 8 и не более 14 символов",),
            (
                "q1!W2@e3#R4$t5%",
                "Длина пароля должна быть не менее 8 и не более 14 символов",
            ),
            ("1", "Пароль должен содержать хотя бы две буквы"),
            ("1234567", "Пароль должен содержать хотя бы две буквы"),
            ("12345678", "Пароль должен содержать хотя бы две буквы"),
            ("1.3<5[6]7", "Пароль должен содержать хотя бы две буквы"),
            (",./<>?';:", "Пароль должен содержать хотя бы две буквы"),
            ("abcdefhg", "Пароль должен содержать хотя бы одну цифру"),
            ("a.b!c@d#e%f&", "Пароль должен содержать хотя бы одну цифру"),
            ("A.b!c@d#e%f&", "Пароль должен содержать хотя бы одну цифру"),
            ("abcdefg1", "Пароль должен содержать хотя бы один знак препинания",),
            ("Abcdefg1", "Пароль должен содержать хотя бы один знак препинания",),
            ("1234567a", "Пароль должен содержать хотя бы один знак препинания",),
            ("1234567a.", "Пароль должен содержать буквы в разных регистрах"),
            ("1234567A.", "Пароль должен содержать буквы в разных регистрах"),
            ("abcdef1.", "Пароль должен содержать буквы в разных регистрах"),
            ("ABCDEF1.", "Пароль должен содержать буквы в разных регистрах"),
            ("абвг@д.Е1", "Буквы могут быть только латинскими",),  # russian letters
            ("абвг@д.Z1", "Буквы могут быть только латинскими",),  # russian letters
            ("q1!W2@ê3#R", "Буквы могут быть только латинскими"),  # french ê
        ],
    )
    def test_register_invalid_password(self, string, client, register_data, message):
        """String passed to password field is not valid."""
        with client:
            register_data["password"] = string
            response: Response = client.post(
                BASE_URL, data=register_data, follow_redirects=True
            )
            assert message in response.get_data(as_text=True)


if __name__ == "__main__":
    pytest.main()
