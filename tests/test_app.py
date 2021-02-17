"""Test app initiation."""

import pytest
from web_shop import app
from web_shop.views import index


def test_index():
    """Test get-index.

    :return assertion
    """
    tester = app.test_client()
    response = tester.get("/", content_type="html/text")
    assert response.status_code == 200
    assert response.data == b"Hello, World!"


if __name__ == "__main__":
    pytest.main()
