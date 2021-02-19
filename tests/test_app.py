"""Test app initiation."""
from bs4 import BeautifulSoup
import pytest
from web_shop import app
from web_shop.views import index


def test_index():
    """Test get-index.

    :return assertion
    """
    app.testing = True
    tester = app.test_client()
    response = tester.get("/", content_type="html/text")
    assert response.status_code == 200
    response.text = BeautifulSoup(response.data, "html.parser").text
    assert "Добро пожаловать в магазин WebShop" in response.text


if __name__ == "__main__":
    pytest.main()
