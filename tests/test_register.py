"""Test registration."""
import pytest
from bs4 import BeautifulSoup
from flask import Response, request, url_for

from web_shop.database import User


class TestRegister:
    """Tests for register-view."""

    def test_get_register(self, client):
        """Test get-register.

        :return assertion
        """
        with client:
            response = client.get("/register", content_type="html/text")
        assert response.status_code == 200
        response.text = BeautifulSoup(response.data, "html.parser").text
        assert response.text.lower().count("регистрация") == 3

    @pytest.mark.xfail
    def test_post_register_normal(self, client):
        """Test normal registration of a new user. Follow redirection.

        Marked xfail for git actions.
        """
        data = dict(
            first_name="test_name",
            last_name="test_surname",
            email="email@email.com",
            password="password",
            password_confirm="password",
            user_type="shop",
        )
        assert not User.query.filter_by(email=data["email"]).first()

        with client:
            response: Response = client.post("/register", data=data, follow_redirects=True)
            assert response.status_code == 200
            assert "Регистрация прошла успешно!" in response.get_data(as_text=True)
            assert request.path == url_for("index")
            user = User.query.filter_by(email=data["email"]).first()
            assert user.user_type.name == data["user_type"]
            assert user.is_active is False
            assert user.confirmed_at is None

    @pytest.mark.xfail
    def test_post_register_normal_no_redirect(self, client):
        """Test normal registration of a new user. No redirection.

        Marked xfail for git actions.
        """
        data = dict(
            first_name="test_name",
            last_name="test_surname",
            email="email1@email.com",
            password="password",
            password_confirm="password",
            user_type="shop",
        )
        assert not User.query.filter_by(email=data["email"]).first()

        with client:
            response: Response = client.post("/register", data=data, follow_redirects=False)
            assert response.status_code == 302


if __name__ == "__main__":
    pytest.main()
