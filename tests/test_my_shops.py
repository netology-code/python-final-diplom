"""Tests for my_shops_view.py views."""
import io
import os


import pytest
from flask import Response, request, url_for
from werkzeug.datastructures import FileStorage


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


class TestGetUploadNewFile:
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
        params = {"shop": shop_title}
        response: Response = logged_in_seller.get(
            url_for("upload_file", **params), follow_redirects=True,
        )
        assert "Загрузите новый файл с данными" not in response.get_data(True)
        assert "Список моих магазинов" in response.get_data(True)
        # assert request.path == url_for('my_shops')  #  !!! Объект request работает неправильно !!!
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
            ("sho", "Shop2"),
            ("hop", "Shop2"),
            ("shp", "Shop2"),
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
        """Test get upload_file view by logged-in seller with wrong params in query_string."""
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
        # assert request.path == url_for('my_shops')  #  !!! Объект request работает неправильно !!!
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


class TestPostUploadNewFile:
    """Test uploading files."""

    @staticmethod
    @pytest.mark.parametrize(
        ("filename", "message"),
        [
            ("shop1.yam", "Допускаются только файлы формата yaml"),
            ("", "Выберите файл"),
            (None, "Файл не прикреплён"),
        ],
    )
    def test_post_a_file(logged_in_seller, filename, message, test_app):
        """Test different posts for file upload."""
        params = {"shop": "Shop2"}
        try:
            if filename:
                path = os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)
                print()
                print(111, path)
                file = FileStorage(stream=open(path, "rb"), filename=filename,)
                response: Response = logged_in_seller.post(
                    url_for("upload_file", **params),
                    data={"file": file},
                    content_type="multipart/form-data",
                    follow_redirects=True,
                )

            elif filename == "":
                file = FileStorage(stream=io.BytesIO(b""), filename=filename,)
                response: Response = logged_in_seller.post(
                    url_for("upload_file", **params),
                    data={"file": file},
                    content_type="multipart/form-data",
                    follow_redirects=True,
                )

            else:
                response: Response = logged_in_seller.post(
                    url_for("upload_file", **params),
                    content_type="multipart/form-data",
                    follow_redirects=True,
                )
            # print(response.get_data(True))
            assert message in response.get_data(True)

        finally:
            if os.path.exists(test_app.config["UPLOAD_FOLDER"]):
                the_only_file_name = [
                    file
                    for _, _, file in os.walk(test_app.config["UPLOAD_FOLDER"])
                    if file
                ]
                if the_only_file_name:
                    the_only_file_name = the_only_file_name[0][0]
                    assert filename in the_only_file_name

                from shutil import rmtree

                rmtree(test_app.config["UPLOAD_FOLDER"])


if __name__ == "__main__":
    pytest.main()
