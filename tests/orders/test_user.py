import pytest
from rest_framework.test import APIClient
from orders.models import User
from model_bakery import baker


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


@pytest.fixture
def user_factory():
    def factory(*args, **kwargs):
        return baker.make(User, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_create_user(client, user_data, user_factory):
    # Arrange
    user_count = User.objects.count()

    # Act
    request = client.post(path='/api/v1/user/register',
                          data=user_data)

    # Assert
    assert request.status_code == 200
    assert request.json() == {"Status": True}

    user_count += 1
    assert User.objects.count() == user_count

    user_factory(_quantity=10)
    assert User.objects.count() == user_count + 10


@pytest.mark.django_db
def test_user_login(client, user_factory):
    user = user_factory()
    request = client.post('/api/v1/user/login',
                          data={
                              "email": user.email,
                              "password": user.password,
                          },
                          )
    assert request.status_code == 200
