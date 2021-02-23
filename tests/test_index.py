"""Test app initiation."""

import pytest
from flask import Response


def test_get_index_on_start(client):
    """Test get-index.

    :return assertion
    """
    response: Response = client.get("/", content_type="html/text")
    assert response.status_code == 200
    assert "Добро пожаловать в магазин WebShop" in response.get_data(as_text=True)


if __name__ == "__main__":
    pytest.main()
