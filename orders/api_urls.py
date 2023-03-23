from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from django_rest_passwordreset.views import reset_password_request_token, \
    reset_password_confirm

from orders.bascket_views import BasketView
from orders.product_views import PartnerUpdate, ProductsList, \
    ProductsView, SingleProductView, ShopView, ProductInfoViewSet
from orders.user_views import LoginAccount, RegisterAccount, \
    ConfirmAccount, ContactViewSet, EditUser, UserEmailVerify
from orders.views import OrderView

app_name = 'orders'
router = DefaultRouter()
router.register(r'user/contact', ContactViewSet, basename='user')

urlpatterns = [
    path('user/login', LoginAccount.as_view(), name='user-login'),
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path('user/register/confirm',
         ConfirmAccount.as_view(), name='user-register-confirm'),
    path('user/details', EditUser.as_view(), name='user-edit'),
    path('user/verify_email/<uidb64>/<token>/',
         UserEmailVerify.as_view(), name='verify-email'),
    path('user/password_reset', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm',
         reset_password_confirm, name='password-reset-confirm'),
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('token/', obtain_auth_token),

    path('shops', ShopView.as_view(), name='shop-list'),

    path('products', ProductInfoViewSet.as_view(), name='products-category'),
    path('products/list', ProductsList.as_view(), name='products-list'),
    path('products/view', ProductsView.as_view(), name='products-view'),
    path('product/view_by_id', SingleProductView.as_view(), name='product-cart-view'),
    path('products/search', ProductInfoViewSet.as_view(), name='products'),
    path('basket', BasketView.as_view(), name='basket'),
    path('order', OrderView.as_view(), name='order'),

] + router.urls
