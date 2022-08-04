from django.urls import path, include
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from rest_framework.routers import SimpleRouter

from .views import RegisterAccount, LoginAccount, ConfirmAccount, AccountDetails, ContactView, ShopView, CategoryView, \
    ProductInfoView, PartnerUpdate, PartnerState, PartnerOrders, BasketView, OrderView

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

app_name = 'shop'

router = SimpleRouter()
router.register('shops', ShopView)
router.register('categories', CategoryView)
router.register('products', ProductInfoView, basename='products')

urlpatterns = [
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('user/details', AccountDetails.as_view(), name='user-detail'),
    path('user/login', LoginAccount.as_view(), name='user-login'),
    path('user/password_reset', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),
    path('user/contact', ContactView.as_view(), name='user-contact'),
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('partner/state', PartnerState.as_view(), name='partner-state'),
    path('partner/orders', PartnerOrders.as_view(), name='partner-orders'),
    path('basket', BasketView.as_view(), name='basket'),
    path('order', OrderView.as_view(), name='order'),
    path('', include(router.urls)),
    path('schema', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui', SpectacularSwaggerView.as_view(url_name='shop:schema'), name='swagger-ui'),
    path('social', include('social_django.urls')),
] + router.urls