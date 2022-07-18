from django.urls import path, include
from rest_framework import routers

from .views import RegisterAccount, LoginAccount, ConfirmAccount, AccountDetails

app_name = 'shop'

# router = routers.SimpleRouter()
# router.register(r'shops')

urlpatterns = [
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('user/details', AccountDetails.as_view(), name='user-detail'),
    path('user/login', LoginAccount.as_view(), name='user-login'),
]