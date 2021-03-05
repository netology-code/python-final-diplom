"""Tests for account management funtions."""

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
            ("token", "ImFkbWluX3Nob3BAdGVzdC5tYWlsIg.YECyMQ.Kpe_hZG7rbGeHB2S3rV6vVX8OgM"),
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
                url_for("retrieve", **params), content_type="html/text", follow_redirects=False
            )
            assert response.status_code == 404

    @pytest.mark.parametrize(
        "email",
        ["admin_buyer@test.mail", "admin_shop@test.mail", "non_admin_buyer@test.mail", "non_admin_shop@test.mail"],
    )
    def test_get_retrieve_with_expired_tokens(self, client, email):
        """Test get-retrieve with expired tokens."""
        token = create_confirmation_token((email, "retrieve_password", datetime.utcnow().timestamp() - 301))
        with client:
            params = {"token": token}
            response: Response = client.get(
                url_for("retrieve", **params), content_type="html/text", follow_redirects=True
            )
            assert "Ссылка недействительна" in response.get_data(True)
            assert request.path == url_for("retrieve")
            assert "Пароль" not in response.get_data(True)

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
            response: Response = client.post(url_for("retrieve"), data=data, follow_redirects=True)
            assert message in response.get_data(True)
            assert "Пароль" not in response.get_data(True)
            assert request.path == url_for("retrieve")

    @pytest.mark.parametrize(
        "email",
        ["admin_buyer@test.mail", "admin_shop@test.mail", "non_admin_buyer@test.mail", "non_admin_shop@test.mail"],
    )
    def test_post_retrieve_with_args(self, client, email):
        """Test post-retrieve with good emails."""
        with client:
            with patch("web_shop.views.acc_management_view.send_message"):
                data = dict(email=email)
                response: Response = client.post(url_for("retrieve"), data=data, follow_redirects=True)
                assert "Ваш предыдущий пароль был сброшен. Проверьте свою почту." in response.get_data(True)
                assert "Пароль" not in response.get_data(True)
                assert request.path == url_for("index")

    @pytest.mark.parametrize(
        "email",
        ["admin_buyer@test.mail", "admin_shop@test.mail", "non_admin_buyer@test.mail", "non_admin_shop@test.mail"],
    )
    def test_post_retrieve_with_password(self, client, email):
        """Test post-retrieve with good tokens."""
        token = create_confirmation_token((email, "retrieve_password", datetime.utcnow().timestamp()))
        new_password = create_random_password()
        with client:
            data = dict(password=new_password, password_confirm=new_password)
            response: Response = client.post(url_for("retrieve", token=token), data=data, follow_redirects=True)
            assert "Пароль был успешно изменен." in response.get_data(True)
            assert request.path == url_for("login")

            data = dict(email=email, password=new_password)
            client.post(url_for("login"), data=data, follow_redirects=True)
            assert current_user.is_authenticated


if __name__ == "__main__":
    pytest.main()
