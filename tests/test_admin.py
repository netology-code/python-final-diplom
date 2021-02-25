"""Tests for admin-view."""

import pytest
from flask import Response, request, url_for

from web_shop.database import User

URL = "/admin/"


class TestEnterAdmin:
    """Test enter admin panel."""

    def test_get_admin_by_admin(self, login_admin, client):
        """Enter admin panel by admin."""
        with client:
            client.post("/login", data=login_admin, follow_redirects=True)
            response: Response = client.get(URL, content_type="html/text")
            assert request.path == URL
            assert response.status_code == 200
            client.get("/logout")

    def test_get_admin_by_non_admin(self, login_non_admin, client):
        """Enter admin panel by non_admin."""
        with client:
            client.post("/login", data=login_non_admin, follow_redirects=True)
            response: Response = client.get(URL, content_type="html/text", follow_redirects=True)
            assert request.path == url_for("index")
            assert response.status_code == 200
            client.get("/logout")

    def test_get_admin_by_anonymous(self, client):
        """Enter admin panel by anonymous user."""
        with client:
            response: Response = client.get(URL, content_type="html/text")
            assert response.status_code == 302

            response = client.get(URL, content_type="html/text", follow_redirects=True)
            assert response.status_code == 200
            assert request.path == url_for("login")
            assert request.args.get("next") == "admin.index"

    def test_login_admin_by_anonimous_admin(self, login_admin, client):
        """Enter admin panel by admin who was not logged in."""
        with client:
            client.get(URL, content_type="html/text", follow_redirects=True)  # enter admin panel as anonymous
            response: Response = client.post(request.url, data=login_admin, follow_redirects=True)  # login as admin
            assert request.path == URL  # return to admin panel as an authenticated admin
            assert response.status_code == 200
            client.get("/logout")


class TestEnterAdminUsers:
    """Test users view at admin panel."""

    def test_get_admin_users_view(self, login_admin, client):
        """Enter users view at admin panel."""
        with client:
            client.post("/login", data=login_admin, follow_redirects=True)
            response: Response = client.get(URL + "user/", content_type="html/text", follow_redirects=True)
            assert request.path == URL + "user/"
            assert all(i in response.get_data(as_text=True) for i in ("List", "Create", "With selected"))

    def test_get_admin_users_view_user(self, login_admin, client):
        """Enter a user entry at admin-users panel."""
        with client:
            client.post("/login", data=login_admin, follow_redirects=True)
            id = 4
            user = User.query.get(id)
            assert user.email == "non_admin_buyer@test.mail"
            response: Response = client.get(
                URL + f"user/edit/?id={id}", content_type="html/text", follow_redirects=True
            )
            assert user.email in response.get_data(as_text=True)
            fields = list(user.__dict__.keys())
            fields.remove("_sa_instance_state")
            assert all(field in response.get_data(as_text=True) for field in fields)


if __name__ == "__main__":
    pytest.main()
