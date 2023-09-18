from django.urls import path

from backend.views import PartnerUpdate, RegisterAccount, ConfirmAccount, AccountDetails, LoginAccount, Logout, \
    ContactView, ShopsView, CategoryView, ProductInfoView, BasketView, PartnerState, PartnerOrders, OrderView

app_name = 'backend'

urlpatterns = [
    path('partner/update/', PartnerUpdate.as_view(), name='partner-update'),
    path('user/register/', RegisterAccount.as_view(), name='user-register'),
    path('confirm/email/', ConfirmAccount.as_view(), name='confirm-email'),
    path('login/account/', LoginAccount.as_view(), name='login-account'),
    path('account/info/', AccountDetails.as_view(), name='account-info'),
    path('logout/', Logout.as_view(), name='logout'),
    path('user/contact/', ContactView.as_view(), name='contact'),
    path('shops/list/', ShopsView.as_view(), name='shop-list'),
    path('categories/', CategoryView.as_view(), name='categories'),
    path('product/info/', ProductInfoView.as_view(), name='product-info'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('partner/state/', PartnerState.as_view(), name='partner-state'),
    path('partner/orders/', PartnerOrders.as_view(), name='partner-orders'),
    path('order/', OrderView.as_view(), name='order'),
]
