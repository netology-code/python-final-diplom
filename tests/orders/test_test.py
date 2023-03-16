import pytest
from rest_framework.test import APIClient

from orders.models import User


def test_test():
    assert 2 == 2


url = 'http://127.0.0.1:8000/api/v1/'


@pytest.mark.django_db
def test_user():
    # Arrange
    client = APIClient()
    user_count = User.objects.count()

    # Act
    request = client.post(path=f'{url}user/register',
                          data={
                              "first_name": "test",
                              "last_name": "test_last",
                              "email": "test@gmail.com",
                              "password": "adminadmin",
                              "company": "Test",
                              "position": "funcionario",
                              "user_type": "shop",
                          })

    # Assert
    assert request.status_code == 200
    assert request.json() == {
        "Status": True,
    }
    assert User.objects.count() == user_count + 1
