"""Test app initiation."""

import pytest
from flask import Response, request, url_for


def test_get_index_on_start(client):
    """Test get-index.

    :return assertion
    """
    response: Response = client.get(url_for("index"), content_type="html/text")
    assert response.status_code == 200
    assert "Добро пожаловать в магазин WebShop" in response.get_data(as_text=True)


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("admin_buyer@test.mail", "testpass1"),
        ("admin_shop@test.mail", "testpass2"),
        ("non_admin_buyer@test.mail", "testpass3"),
        ("non_admin_shop@test.mail", "testpass4"),
    ],
)
def test_logout(client, username, password):
    """Test logout."""
    with client:
        data = dict(email=username, password=password, remember_me=False)

        response: Response = client.post(
            url_for("login"), data=data, follow_redirects=True
        )
        assert request.path == url_for("index")
        assert "Выйти" in response.get_data(as_text=True)

        response = client.get(url_for("logout"), follow_redirects=True)
        assert request.path == url_for("index")
        assert "Войти" in response.get_data(as_text=True)


if __name__ == "__main__":
    pytest.main()
