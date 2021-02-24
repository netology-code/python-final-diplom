"""Tests for admin-view."""

import pytest
from flask import Response, request, url_for

URL = "/admin/"


def test_get_admin_by_admin(login_admin, client):
    """Enter admin panel by admin."""
    with client:
        client.post("/login", data=login_admin, follow_redirects=True)
        response: Response = client.get(URL, content_type="html/text")
        assert request.path == URL
        assert response.status_code == 200
        client.get("/logout")


def test_get_admin_by_non_admin(login_non_admin, client):
    """Enter admin panel by non_admin."""
    with client:
        client.post("/login", data=login_non_admin, follow_redirects=True)
        response: Response = client.get(URL, content_type="html/text", follow_redirects=True)
        assert request.path == url_for("index")
        assert response.status_code == 200
        client.get("/logout")


def test_get_admin_by_anonymous(client):
    """Enter admin panel by anonymous user."""
    with client:
        response: Response = client.get(URL, content_type="html/text")
        assert response.status_code == 302

        response = client.get(URL, content_type="html/text", follow_redirects=True)
        assert response.status_code == 200
        assert request.path == url_for("login")
        assert request.args.get("next") == "admin.index"


def test_login_by_anonimous_admin(login_admin, client):
    """Enter admin panel by admin who was not logged in."""
    with client:
        client.get(URL, content_type="html/text", follow_redirects=True)  # enter admin panel as anonymous
        response: Response = client.post(request.url, data=login_admin, follow_redirects=True)  # login as admin
        assert request.path == URL  # return to admin panel as an authenticated admin
        assert response.status_code == 200
        client.get("/logout")


if __name__ == "__main__":
    pytest.main()
