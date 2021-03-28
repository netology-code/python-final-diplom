"""Tests for account management functions."""

from datetime import datetime
from string import ascii_lowercase, ascii_uppercase, digits, punctuation
from unittest.mock import patch

import pytest
from flask import Response, request, url_for
from flask_login import current_user

from web_shop.database import User
from web_shop.emails import create_confirmation_token
from web_shop.views.acc_management_view import (
    create_random_password,
    get_random_password_hash,
    retrieve_password,
)


class TestGetRandomPassword:
    """Test random password functions."""

    def test_get_random_password(self, client):
        """Test two passwords are different."""
        for _ in range(5):
            result = create_random_password()
            assert all(
                (
                    any(el in ascii_uppercase for el in result),
                    any(el in ascii_lowercase for el in result),
                    any(el in digits for el in result),
                    any(el in punctuation for el in result),
                )
            )

    def test_get_random_password_difference(self, client):
        """Test two passwords are different."""
        for _ in range(5):
            result = create_random_password()
            result1 = create_random_password()
            assert result != result1

    def test_get_random_password_hash_call(self, client):
        """Test random password makes a hash-string."""
        for _ in range(5):
            result = get_random_password_hash()
            mode, hash_type, iterations = result.split("$")[0].split(":")
            assert mode == "pbkdf2"
            assert hash_type == "sha256"
            assert int(iterations) == 150000
            assert len(result) == 94

    def test_get_random_password_hash_difference(self, client):
        """Test two passwords hashes are different."""
        for _ in range(5):
            result = get_random_password_hash()
            result1 = get_random_password_hash()
            assert result != result1


class TestRetrievePassword:
    """Test retrieve_password function."""

    def test_retrieve_password_call(self, client, database):
        """Test retrieve_password call changes user password."""
        user: User = User.query.get(1)
        old_password = user.password
        with patch("web_shop.views.acc_management_view.send_message"):
            retrieve_password(user)
        del user
        new_user_params: User = User.query.get(1)
        assert old_password != new_user_params.password


class TestRetrieve:
    """Test retrieve view."""

    URL = "/retrieve"

    def test_get_retrieve(self, client):
        """Test get-retrieve."""
        with client:
            response: Response = client.get(self.URL, content_type="html/text")
            assert response.status_code == 200
            assert "Восстановление доступа" in response.get_data(as_text=True)
            assert "Пароль" not in response.get_data(as_text=True)

    @pytest.mark.parametrize(
        ("arg_name", "arg"),
        [
            ("", ""),
            ("arg", ""),
            ("arg", "arg"),
            ("1", "1"),
            ("132", "123"),
            ("token", ""),
            ("token", "token"),
            ("token", "ImFkbWluX3Nob3BAdGVzdC5tYWlsIg"),
            ("token", "ImFkbWluX3Nob3BAdGVzdC5tYWlsIg.YECyMQ"),
            (
                "token",
                "ImFkbWluX3Nob3BAdGVzdC5tYWlsIg.YECyMQ.Kpe_hZG7rbGeHB2S3rV6vVX8OgM",
            ),
            ("token", "YECyMQ.Kpe_hZG7rbGeHB2S3rV6vVX8OgM"),
            ("token", "Kpe_hZG7rbGeHB2S3rV6vVX8OgM"),
            ("token", "123.456.789"),
        ],
    )
    def test_get_retrieve_with_bad_args(self, client, arg_name, arg):
        """Test get-retrieve with unexpected args."""
        with client:
            params = {arg_name: arg}
            response: Response = client.get(
                url_for("retrieve", **params),
                content_type="html/text",
                follow_redirects=False,
            )
            assert response.status_code == 404

    @pytest.mark.parametrize(
        "email",
        [
            "admin_buyer@test.mail",
            "admin_shop@test.mail",
            "non_admin_buyer@test.mail",
            "non_admin_shop@test.mail",
        ],
    )
    def test_get_retrieve_with_expired_tokens(self, client, email):
        """Test get-retrieve with expired tokens."""
        token = create_confirmation_token(
            (email, "retrieve_password", datetime.utcnow().timestamp() - 301)
        )
        with client:
            params = {"token": token}
            response: Response = client.get(
                url_for("retrieve", **params),
                content_type="html/text",
                follow_redirects=True,
            )
            assert "Ссылка недействительна" in response.get_data(True)
            assert request.path == url_for("retrieve")
            assert "Пароль" not in response.get_data(True)
            print(request.__dict__)

    @pytest.mark.parametrize(
        ("email", "message"),
        [
            ("", "Адрес не указан"),
            ("a", "Пользователь не зарегистрирован"),
            ("1", "Пользователь не зарегистрирован"),
            ("123", "Пользователь не зарегистрирован"),
            ("ruru@ru.ru", "Пользователь не зарегистрирован"),
        ],
    )
    def test_post_retrieve_with_bad_args(self, client, email, message):
        """Test post-retrieve with bad emails."""
        with client:
            data = dict(email=email)
            response: Response = client.post(
                url_for("retrieve"), data=data, follow_redirects=True
            )
            assert message in response.get_data(True)
            assert "Пароль" not in response.get_data(True)
            assert request.path == url_for("retrieve")

    @pytest.mark.parametrize(
        "email",
        [
            "admin_buyer@test.mail",
            "admin_shop@test.mail",
            "non_admin_buyer@test.mail",
            "non_admin_shop@test.mail",
        ],
    )
    def test_post_retrieve_with_args(self, client, email):
        """Test post-retrieve with good emails."""
        with client:
            with patch("web_shop.views.acc_management_view.send_message"):
                data = dict(email=email)
                response: Response = client.post(
                    url_for("retrieve"), data=data, follow_redirects=True
                )
                assert (
                    "Ваш предыдущий пароль был сброшен. Проверьте свою почту."
                    in response.get_data(True)
                )
                assert "Пароль" not in response.get_data(True)
                assert request.path == url_for("index")

    @pytest.mark.parametrize(
        "email",
        [
            "admin_buyer@test.mail",
            "admin_shop@test.mail",
            "non_admin_buyer@test.mail",
            "non_admin_shop@test.mail",
        ],
    )
    def test_post_retrieve_with_password(self, client, email):
        """Test post-retrieve with good tokens."""
        token = create_confirmation_token(
            (email, "retrieve_password", datetime.utcnow().timestamp())
        )
        new_password = create_random_password()
        with client:
            data = dict(password=new_password, password_confirm=new_password)
            response: Response = client.post(
                url_for("retrieve", token=token), data=data, follow_redirects=True,
            )
            assert "Пароль был успешно изменен." in response.get_data(True)
            assert request.path == url_for("login")

            data = dict(email=email, password=new_password)
            client.post(url_for("login"), data=data, follow_redirects=True)
            assert current_user.is_authenticated


class TestGetPersonalAccount:
    """Test GET personal account pages."""

    def test_get_account_after_login(self, login_admin, client):
        """Enter personal account in normal way."""
        with client:
            client.post("/login", data=login_admin, follow_redirects=True)
            response: Response = client.get(url_for("account"))
            message = f"Добрый день {current_user.first_name}! Добро пожаловать в личный кабинет!"
            assert message in response.get_data(True)
            assert request.path == url_for("account")

    def test_get_account_without_login(self, login_admin, client):
        """Enter personal account being not logged in."""
        with client:
            response: Response = client.get(url_for("account"), follow_redirects=True)
            assert request.path != url_for("account")
            assert request.path == url_for("login")
            message = "Добро пожаловать в личный кабинет!"
            assert message not in response.get_data(True)

    def test_get_edit_account_after_login(self, login_admin, client):
        """Enter personal account edit page with no args in query."""
        with client:
            client.post("/login", data=login_admin, follow_redirects=True)
            response: Response = client.get("/account/edit", follow_redirects=True)
            assert response.status_code == 404

    def test_get_edit_name_account_after_login(self, login_admin, client):
        """Enter edit name page."""
        with client:
            client.post("/login", data=login_admin, follow_redirects=True)
            response: Response = client.get("/account/edit?name", follow_redirects=True)
            assert response.status_code == 200
            assert "Имя" in response.get_data(True)
            assert "Фамилия" in response.get_data(True)

    def test_get_edit_name_account_before_login(self, login_admin, client):
        """Enter edit name page being not logged in."""
        with client:
            client.get("/account/edit?name", follow_redirects=True)
            assert request.path == url_for("login")


class TestPostPersonalAccountName:
    """Test change personal account name data."""

    def test_post_edit_name_account_after_login(self, login_non_admin, client):
        """Post new full name data in edit name page."""
        with client:
            client.post("/login", data=login_non_admin, follow_redirects=True)
            assert current_user.first_name != "Bill"
            assert current_user.last_name != "Gates"
            data = dict(first_name="Bill", last_name="Gates")
            response: Response = client.post(
                "/account/edit?name", data=data, follow_redirects=True
            )
            assert request.path == url_for("account")
            assert "Bill" in response.get_data(True)
            assert "Gates" in response.get_data(True)
            assert current_user.first_name == "Bill"
            assert current_user.last_name == "Gates"

    def test_post_edit_first_name_account_after_login(self, login_admin, client):
        """Post new first name data in edit name page."""
        with client:
            client.post("/login", data=login_admin, follow_redirects=True)
            assert current_user.first_name != "Bill"
            data = dict(first_name="Bill")
            response: Response = client.post(
                "/account/edit?name", data=data, follow_redirects=True
            )
            assert request.path == url_for("account")
            assert "Bill" in response.get_data(True)
            assert "Gates" not in response.get_data(True)
            assert current_user.first_name == "Bill"

    def test_post_edit_last_name_account_after_login(self, login_admin, client):
        """Post new last name data in edit name page."""
        with client:
            client.post("/login", data=login_admin, follow_redirects=True)
            assert current_user.last_name != "Gates"
            data = dict(last_name="Gates")
            response: Response = client.post(
                "/account/edit?name", data=data, follow_redirects=True
            )
            assert request.path == url_for("account")
            assert "Gates" in response.get_data(True)
            assert current_user.last_name == "Gates"


class TestPostPersonalAccountEmail:
    """Test change personal account email data."""

    def test_post_edit_email_account_after_login(self, login_non_admin, client):
        """Post new email data in edit email page."""
        with client:
            new_email = "no_email@email.ru"
            client.post("/login", data=login_non_admin, follow_redirects=True)
            assert current_user.email != new_email
            data = dict(email=new_email)
            response: Response = client.post(
                "/account/edit?email", data=data, follow_redirects=True
            )
            assert request.path == url_for("account")
            assert new_email in response.get_data(True)
            assert current_user.email == new_email

            client.get(url_for("logout"))
            login_non_admin["email"] = new_email
            client.post("/login", data=login_non_admin, follow_redirects=True)
            assert current_user.is_authenticated

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
    def test_post_edit_invalid_email_account_after_login(
        self, client, login_admin, string, message
    ):
        """String passed to email field is not valid."""
        with client:
            client.post("/login", data=login_admin, follow_redirects=True)
            response: Response = client.post(
                "/account/edit?email", data={"email": f"{string}"}, follow_redirects=True,
            )
            assert message in response.get_data(as_text=True)


class TestPostPersonalAccountPassword:
    """Test change personal account  password data."""

    def test_post_edit_password_account_after_login(self, login_admin, client):
        """Post new password data in edit password page."""
        with client:
            new_password = "QwErTy0="
            client.post("/login", data=login_admin, follow_redirects=True)
            data = dict(password=new_password, password_confirm=new_password)

            client.post("/account/edit?password", data=data, follow_redirects=True)
            assert request.path == url_for("account")

            client.get(url_for("logout"))

            login_admin["password"] = new_password
            client.post("/login", data=login_admin, follow_redirects=True)
            assert current_user.is_authenticated

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
    def test_post_edit_invalid_password_confirmation_account_after_login(
        self, client, login_non_admin, password, password_confirm
    ):
        """String passed to password and password_confirm fields do not match each other."""
        with client:
            client.post("/login", data=login_non_admin, follow_redirects=True)
            response: Response = client.post(
                "/account/edit?password",
                data={"password": f"{password}", "password_confirm": password_confirm},
                follow_redirects=True,
            )
            assert "Пароли не совпадают" in response.get_data(as_text=True)

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
    def test_post_edit_invalid_password_account_after_login(
        self, client, login_non_admin, string, message
    ):
        """String passed to password is invalid password."""
        with client:
            client.post("/login", data=login_non_admin, follow_redirects=True)
            response: Response = client.post(
                "/account/edit?password",
                data={"password": string, "password_confirm": string},
                follow_redirects=True,
            )
            assert message in response.get_data(as_text=True)


class TestGetPersonalAccountStatus:
    """Test change personal account activity status data."""

    def test_get_personal_account_status_change1(self, client, login_admin):
        """Test inactive user becomes active."""
        with client:
            client.post("/login", data=login_admin, follow_redirects=True)
            assert not current_user.is_active
            client.get("/account/edit?status")
            assert current_user.is_active

    def test_get_personal_account_status_change2(self, client, login_non_admin):
        """Test active user becomes inactive."""
        with client:
            client.post("/login", data=login_non_admin, follow_redirects=True)
            assert current_user.is_active
            client.get("/account/edit?status")
            assert not current_user.is_active


class TestCancelPersonalAccount:
    """Test for cancel button in personal account pages."""

    @pytest.mark.parametrize(
        "url", ["/account/edit?name", "/account/edit?password", "/account/edit?email"],
    )
    def test_cancel_personal_account_name_change(self, client, login_admin, url):
        """Test active user becomes inactive."""
        with client:
            client.post("/login", data=login_admin, follow_redirects=True)
            response: Response = client.get(url)
            assert "Тип пользователя:" not in response.get_data(True)
            response_cancel: Response = client.post(
                url, data={"cancel": "cancel"}, follow_redirects=True
            )
            assert response.get_data(True) != response_cancel.get_data(True)
            assert "Тип пользователя:" in response_cancel.get_data(True)


if __name__ == "__main__":
    pytest.main()
