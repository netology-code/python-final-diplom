"""Tests for my_shops.py views."""

import pytest
from flask import Response, request, url_for


class TestGetMyShops:
    """Tests for my_shops view."""

    @staticmethod
    def test_get_my_shops(logged_in_seller):
        """Test get my_shops view by logged in seller."""
        response: Response = logged_in_seller.get(
            url_for("my_shops"), follow_redirects=True
        )
        assert "Список моих магазинов" in response.get_data(True)
        assert "Подключить новый магазин" in response.get_data(True)

    @staticmethod
    def test_get_my_shops_by_customer(logged_in_customer):
        """Test get my_shops view by logged in customer."""
        response: Response = logged_in_customer.get(
            url_for("my_shops"), follow_redirects=True
        )
        assert "Список моих магазинов" not in response.get_data(True)
        assert "Подключить новый магазин" not in response.get_data(True)
        assert request.path == url_for("index")

    @staticmethod
    def test_get_my_shops_by_anonymous(client):
        """Test get my_shops view by anonymous user."""
        response: Response = client.get(url_for("my_shops"), follow_redirects=True)
        assert "Список моих магазинов" not in response.get_data(True)
        assert "Подключить новый магазин" not in response.get_data(True)
        assert request.path == url_for("index")


class TestUploadNewFile:
    """Tests for upload_file view."""

    @staticmethod
    @pytest.mark.parametrize("shop_title", ["Shop2", "Shop3"])
    def test_get_upload_new_file(logged_in_seller, shop_title):
        """Test get upload_file view by logged in customer."""
        response: Response = logged_in_seller.get(
            url_for("upload_file") + f"?shop={shop_title}", follow_redirects=True
        )
        assert "Загрузите новый файл с данными" in response.get_data(True)

    @staticmethod
    @pytest.mark.parametrize(
        "shop_title", ["Shop", "Shop1", "", " ", "_", 1, 0, -1, None, True, False],
    )
    def test_get_upload_new_file_wrong_params(logged_in_seller, shop_title):
        """Test get upload_file view by logged in seller with wrong params in query_string value."""
        params = {"shop": {shop_title}}
        response: Response = logged_in_seller.get(
            url_for("upload_file", **params), follow_redirects=True,
        )
        assert "Загрузите новый файл с данными" not in response.get_data(True)
        assert "Список моих магазинов" in response.get_data(True)
        # assert request.path == url_for('my_shops')
        # print(request.__dict__)

    @staticmethod
    @pytest.mark.parametrize(
        ("query_key", "query_val"),
        [
            ("Shop", "Shop2"),
            ("sHop", "Shop2"),
            ("shOp", "Shop2"),
            ("shoP", "Shop2"),
            ("SHOP", "Shop2"),
            ("sHoP", "Shop2"),
            ("ShOp", "Shop2"),
            ("sHOp", "Shop2"),
            ("ShoP", "Shop2"),
            ("SHOp", "Shop2"),
            ("sHOP", "Shop2"),
            ("ShOP", "Shop2"),
            ("SHoP", "Shop2"),
            ("", ""),
            ("", " "),
            (" ", " "),
            (" ", ""),
            ("_", 1),
            (0, -1),
            (None, None),
            (None, True),
            (None, False),
            (True, None),
            ("True", "True"),
            (True, False),
            (False, None),
            (False, True),
            (False, False),
        ],
    )
    def test_get_upload_new_file_wrong_query_string(
        logged_in_seller, query_key, query_val
    ):
        """Test get upload_file view by logged in seller with wrong params in query_string."""
        params = {query_key: query_val} if query_key and query_val else None
        if params:
            response: Response = logged_in_seller.get(
                url_for("upload_file", **params), follow_redirects=True,
            )
        else:
            response: Response = logged_in_seller.get(
                url_for("upload_file"), follow_redirects=True,
            )
        assert "Загрузите новый файл с данными" not in response.get_data(True)
        assert "Список моих магазинов" in response.get_data(True)
        # assert request.path == url_for('my_shops')
        # print(request.__dict__)

    @staticmethod
    def test_get_upload_new_file_by_customer(logged_in_customer):
        """Test get upload_file view by logged in customer."""
        response: Response = logged_in_customer.get(
            url_for("upload_file"), follow_redirects=True
        )
        assert "Загрузите новый файл с данными" not in response.get_data(True)
        assert request.path == url_for("index")

    @staticmethod
    def test_get_upload_new_file_by_anonymous(client):
        """Test get upload_file view by logged in customer."""
        response: Response = client.get(url_for("upload_file"), follow_redirects=True)
        assert "Загрузите новый файл с данными" not in response.get_data(True)
        assert request.path == url_for("index")


if __name__ == "__main__":
    pytest.main()
