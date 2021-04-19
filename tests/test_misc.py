"""Tests for different functions."""
import time
from unittest.mock import patch

from flask_mail import Message

import pytest
from flask import Response, request, url_for
from itsdangerous import SignatureExpired

from web_shop.database import User
from web_shop import token_serializer
from web_shop.emails import create_confirmation_token, create_message
from web_shop.views import confirm
from web_shop.views.my_shops_view import allowed_file


class TestEmailSender:
    """Test emails module."""

    @pytest.mark.parametrize(
        ("email", "expiry_time"),
        [("non_admin_buyer@test.mail", 1), ("admin_shop@test.mail", 2)],
    )
    def test_create_confirmation_token(self, test_app, email, expiry_time):
        token = create_confirmation_token(email)
        if expiry_time > 1:
            stored_email = token_serializer.loads(
                token, salt=test_app.config["SECRET_KEY"]
            )
            assert stored_email == email
        else:
            time.sleep(2)
            with pytest.raises(SignatureExpired):
                token_serializer.loads(
                    token, salt=test_app.config["SECRET_KEY"], max_age=expiry_time,
                )

    @pytest.mark.parametrize(
        "email", ["non_admin_buyer@test.mail", "admin_shop@test.mail"]
    )
    def test_create_message(self, email):
        message = create_message(f"Test_email_{email}", email)
        assert isinstance(message, Message)
        assert email in message.subject
        assert message.recipients == [email]

    @pytest.mark.parametrize(
        "email", ["non_admin_buyer@test.mail", "admin_shop@test.mail"]
    )
    def test_body_message(self, email):
        message = create_message("", email)
        token = create_confirmation_token(email)
        link = url_for("confirm", token=token, _external=True)
        message.body = f"Link in body {link}"
        assert link in message.body

    @pytest.mark.parametrize("email", ["new_user1@test.mail", "new_user2@test.mail"])
    def test_confirm_email_non_users(self, email, client):
        """Confirmation url got by an unregistered user."""
        token = create_confirmation_token(email)
        link = url_for("confirm", token=token, _external=True)
        with client:
            response: Response = client.get(
                link, content_type="html/text", follow_redirects=True
            )
            assert request.path == url_for("register")
            assert "Ссылка недействительна. Пройдите регистрацию." in response.get_data(
                True
            )

    @pytest.mark.parametrize(
        "email", ["admin_shop@test.mail", "non_admin_buyer@test.mail"]
    )
    def test_confirm_email_confirmed_users(self, email, client):
        """Confirmation url got by an unregistered user."""
        token = create_confirmation_token(email)
        link = url_for("confirm", token=token, _external=True)
        with client:
            response: Response = client.get(
                link, content_type="html/text", follow_redirects=True
            )
            assert request.path == url_for("login")
            assert (
                "Ссылка недействительна. Пройдите регистрацию."
                not in response.get_data(True)
            )

    @pytest.mark.parametrize(
        "email", ["admin_shop@test.mail", "non_admin_buyer@test.mail"]
    )
    def test_confirm_email_expired_confirmation_old_users(
        self, email, register_data, client
    ):
        """Confirmation url got by an old confirmed user."""
        register_data["email"] = email
        token = create_confirmation_token(email)
        time.sleep(2)
        confirm(token, 1)
        assert User.query.filter_by(email=email).first()

    @pytest.mark.parametrize("email", ["new_user1@test.mail", "new_user2@test.mail"])
    def test_confirm_email_new_users(self, email, register_data, client):
        """Confirmation url got by a new user."""
        register_data["email"] = email
        token = create_confirmation_token(email)
        link = url_for("confirm", token=token, _external=True)
        with client:
            with patch("web_shop.views.register_view.send_message"):
                client.post(
                    url_for("register"), data=register_data, follow_redirects=True,
                )
                response: Response = client.get(
                    link, content_type="html/text", follow_redirects=True
                )
                assert request.path == url_for("login")
                assert "Учётная запись подтверждена" in response.get_data(True)
                user = User.query.filter_by(email=email).first()
                assert user.is_active

    @pytest.mark.parametrize("email", ["new_user3@test.mail", "new_user4@test.mail"])
    def test_confirm_email_expired_confirmation(self, email, register_data, client):
        """Confirmation url got by a new user too late."""
        register_data["email"] = email
        token = create_confirmation_token(email)
        with client:
            with patch("web_shop.views.register_view.send_message"):
                client.post(
                    url_for("register"), data=register_data, follow_redirects=True,
                )
                assert User.query.filter_by(email=email).first()
                time.sleep(2)
                confirm(token, 1)
                assert not User.query.filter_by(email=email).first()


class TestAllowedFileExtension:
    """Test allowed_file function."""

    @staticmethod
    @pytest.mark.parametrize(
        ("filename", "result"),
        [
            (".yaml", True),
            ("1.yaml", True),
            ("a.yaml", True),
            ("filename.yaml", True),
            ("filename.Yaml", True),
            ("filename.YAml", True),
            ("filename.YAMl", True),
            ("filename.YAML", True),
            ("filename.yAML", True),
            ("filename.yaML", True),
            ("filename.yamL", True),
            ("filename.YaMl", True),
            ("filename.yAmL", True),
            ("filename.YamL", True),
            ("filename.yAMl", True),
            ("", False),
            (" ", False),
            ("filename.yml", False),
            ("filename.yal", False),
            ("filename.yl", False),
            ("filename.doc", False),
            ("filename.exe", False),
            (None, False),
            (True, False),
            (False, False),
            (["filename.yaml"], False),
            ([], False),
            (("filename.yaml",), False),
            (tuple(), False),
        ],
    )
    def test_allowed_file(filename, result):
        """Test only 'yaml' extension is allowed (case-independently)."""
        assert result == allowed_file(filename)


if __name__ == "__main__":
    pytest.main()
