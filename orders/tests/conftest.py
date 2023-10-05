import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

URL_SHOP = 'https://raw.githubusercontent.com/OlegSungyrovsky/python-final-diplom/master/data/shop1.yaml'


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def model_factory():
    def factory(model, *args, **kwargs):
        return baker.make(model, *args, **kwargs)

    return factory


@pytest.fixture
def create_shop_user():
    return get_user_model().objects.create_user(
        email='testcreat@kip.com',
        password='asdhakfosaf',
        is_active=True,
        type='shop',
    )


@pytest.fixture
def create_bayer_user():
    return get_user_model().objects.create_user(
        email='testcreat@kip.com',
        password='asdhakfosaf',
    )


@pytest.fixture
def create_admin_user():
    return get_user_model().objects.create_superuser(
        email='testaassdw@kip.com',
        password='asdhakfosaf',
        is_active=True
    )


@pytest.fixture
def create_user_is_active():
    return get_user_model().objects.create_user(
        email='testasdw@kip.com',
        password='asdhakfosaf',
        is_active=True,
    )


@pytest.fixture
def get_token(db, create_user_is_active):
    user = create_user_is_active
    token, _ = Token.objects.get_or_create(user=user)
    return token


@pytest.fixture
def get_shop_token(db, create_shop_user):
    user = create_shop_user
    token, _ = Token.objects.get_or_create(user=user)
    return token


@pytest.fixture
def get_admin_token(db, create_admin_user):
    user = create_admin_user
    token, _ = Token.objects.get_or_create(user=user)
    return token


def headers_token(token: Token) -> dict:
    return {
        'Authorization': f'Token {token.key}'
    }
