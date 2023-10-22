from django.urls import path
from django_rest_passwordreset.views import reset_password_confirm, reset_password_request_token

from backend.views import (AccountDetails, AdminView, BasketView, CategoryView, ConfirmAccount, ContactView,
                           LoginAccount, Logout, OrderView, PartnerOrders, PartnerState, PartnerUpdate,
                           ProductInfoView, RegisterAccount, ShopsView, CreateNewUserImage, CreateNewProductInfoImage)

app_name = 'backend'

urlpatterns = [
    path('user/register/', RegisterAccount.as_view(), name='user-register'),
    path('user/password_reset/', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm/', reset_password_confirm, name='password-reset-confirm'),
    path('user/contact/', ContactView.as_view(), name='contact'),
    path('confirm/email/', ConfirmAccount.as_view(), name='confirm-email'),
    path('login/account/', LoginAccount.as_view(), name='login-account'),
    path('login/account/image/', CreateNewUserImage.as_view(), name='account-image'),
    path('logout/', Logout.as_view(), name='logout'),
    path('account/info/', AccountDetails.as_view(), name='account-info'),
    path('partner/update/', PartnerUpdate.as_view(), name='partner-update'),
    path('partner/state/', PartnerState.as_view(), name='partner-state'),
    path('partner/orders/', PartnerOrders.as_view(), name='partner-orders'),
    path('shops/list/', ShopsView.as_view(), name='shop-list'),
    path('categories/', CategoryView.as_view(), name='categories'),
    path('product/info/', ProductInfoView.as_view(), name='product-info'),
    path('product/info/image/', CreateNewProductInfoImage.as_view(), name='product-image'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('order/', OrderView.as_view(), name='order'),
    path('order/<int:pk>/', OrderView.as_view(), name='order_pk'),
    path('admin/', AdminView.as_view(), name='admin'),
]
