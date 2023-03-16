import pytest
from rest_framework.test import APIClient
from orders.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "first_name": "test",
        "last_name": "test_last",
        "email": "test@gmail.com",
        "password": "adminadmin",
        "company": "Test",
        "position": "funcionario",
        "user_type": "shop",
    }


@pytest.mark.django_db
def test_create_user(client, user_data):
    # Arrange
    user_count = User.objects.count()

    # Act
    request = client.post(path='/api/v1/user/register',
                          data=user_data)

    # Assert
    assert request.status_code == 200
    assert request.json() == {
        "Status": True,
    }
    assert User.objects.count() == user_count + 1
