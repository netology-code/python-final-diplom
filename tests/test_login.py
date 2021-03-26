"""Test login."""

import pytest
from flask import Response, request, url_for
from flask_login import current_user


class TestNormalLogin:
    """Tests for normal login of existing users."""

    def test_get_login(self, client):
        """Test get-login."""
        with client:
            response: Response = client.get("/login", content_type="html/text")
            assert response.get_data(as_text=True).lower().count("вход") == 2

    def test_get_login_logged_in(self, client, login_admin):
        """Test get-login by logged-in user."""
        with client:
            client.post("/login", data=login_admin, follow_redirects=True)
            assert current_user.is_authenticated
            client.get("/login", content_type="html/text", follow_redirects=True)
            assert request.path == url_for("index")

    @pytest.mark.parametrize(
        ("username", "pwd", "is_admin", "user_type"),
        [
            ("admin_buyer@test.mail", "testpass1", True, "customer"),
            ("admin_shop@test.mail", "testpass2", True, "seller"),
            ("non_admin_buyer@test.mail", "testpass3", False, "customer"),
            ("non_admin_shop@test.mail", "testpass4", False, "seller"),
        ],
    )
    def test_login_post_form_existing_users_no_redirection(
        self, username, pwd, is_admin, user_type, client
    ):
        """Test logging in for existing users with confirmed emails. Catch redirect code with no redirection."""
        with client:
            response: Response = client.post(
                "/login",
                data=dict(email=username, password=pwd, remember_me=False),
                follow_redirects=False,
            )
            assert response.status_code == 302
            assert current_user.is_admin == is_admin
            assert current_user.user_type.name == user_type
            assert "Админка" not in response.get_data(as_text=True)
            client.get("/logout")

    @pytest.mark.parametrize(
        ("username", "pwd", "is_admin", "user_type"),
        [
            ("admin_buyer@test.mail", "testpass1", True, "customer"),
            ("admin_shop@test.mail", "testpass2", True, "seller"),
            ("non_admin_buyer@test.mail", "testpass3", False, "customer"),
            ("non_admin_shop@test.mail", "testpass4", False, "seller"),
        ],
    )
    def test_login_post_form_existing_users_redirection(
        self, username, pwd, is_admin, user_type, client
    ):
        """Test logging in for existing active users with confirmed emails. Follow redirection."""
        with client:
            response: Response = client.post(
                "/login",
                data=dict(email=username, password=pwd, remember_me=False),
                follow_redirects=True,
            )
            assert response.status_code == 200
            assert current_user.user_type.name == user_type
            assert ("Админка" in response.get_data(as_text=True)) == is_admin
            assert (
                "Проверьте почту и активируйте учётную запись"
                not in response.get_data(as_text=True)
            )
            assert request.path == url_for("index")
            client.get("/logout")

    @pytest.mark.parametrize(
        ("username", "pwd"),
        [
            ("admin_buyer_unc@test.mail", "testpass1"),
            ("admin_shop_unc@test.mail", "testpass2"),
            ("non_admin_buyer_unc@test.mail", "testpass3"),
            ("non_admin_shop_unc@test.mail", "testpass4"),
        ],
    )
    def test_login_post_form_existing_unconfirmed_users_redirection(
        self, username, pwd, client
    ):
        """Test logging in for existing not active users. Follow redirection."""
        with client:
            response: Response = client.post(
                "/login",
                data=dict(email=username, password=pwd, remember_me=False),
                follow_redirects=True,
            )
            assert request.path == url_for("index")
            assert current_user.is_active is False
            assert "Проверьте почту и активируйте учётную запись" in response.get_data(
                as_text=True
            )
            client.get("/logout")


class TestFailedLogin:
    """Tests for failed login of existing users due to mistakes in credentials."""

    def test_login_empty_form(self, client):
        """Test empty form is submitted."""
        with client:
            response: Response = client.post(
                "/login",
                data=dict(email="", password="", remember_me=False),
                follow_redirects=True,
            )
            assert "Адрес и пароль не указаны" in response.get_data(as_text=True)
            assert request.path == url_for("login")
            assert current_user.is_anonymous

    def test_login_no_email(self, client):
        """Test form with no email is submitted."""
        with client:
            response: Response = client.post(
                "/login",
                data=dict(email="", password="testpass1", remember_me=False),
                follow_redirects=True,
            )
            assert "Адрес не указан" in response.get_data(as_text=True)
            assert request.path == url_for("login")
            assert current_user.is_anonymous

    def test_login_no_password(self, client):
        """Test form with no password is submitted."""
        with client:
            response: Response = client.post(
                "/login",
                data=dict(email="admin_buyer@test.mail", password="", remember_me=False,),
                follow_redirects=True,
            )
            assert "Пароль не указан" in response.get_data(as_text=True)
            assert request.path == url_for("login")
            assert current_user.is_anonymous

    def test_login_wrong_email(self, client):
        """Test wrong email is submitted."""
        with client:
            response: Response = client.post(
                "/login",
                data=dict(
                    email="admin_buyer@test.mai_",
                    password="testpass1",
                    remember_me=False,
                ),
                follow_redirects=True,
            )
            assert "Пользователь не зарегистрирован" in response.get_data(as_text=True)
            assert request.path == url_for("login")
            assert current_user.is_anonymous

    def test_login_wrong_password(self, client):
        """Test wrong password is submitted."""
        with client:
            response: Response = client.post(
                "/login",
                data=dict(
                    email="admin_buyer@test.mail",
                    password="testpass1_",
                    remember_me=False,
                ),
                follow_redirects=True,
            )
            assert "Ошибка при вводе пароля" in response.get_data(as_text=True)
            assert request.path == url_for("login")
            assert current_user.is_anonymous

    def test_login_wrong_credentials(self, client):
        """Test wrong credentials are submitted."""
        with client:
            response: Response = client.post(
                "/login",
                data=dict(
                    email="admin_buyer@test.mai_",
                    password="testpass1_",
                    remember_me=False,
                ),
                follow_redirects=True,
            )
            assert "Пользователь не зарегистрирован" in response.get_data(as_text=True)
            assert request.path == url_for("login")
            assert current_user.is_anonymous


if __name__ == "__main__":
    pytest.main()
