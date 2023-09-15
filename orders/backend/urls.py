from django.urls import path

from backend.views import PartnerUpdate, RegisterAccount, ConfirmAccount, AccountDetails, LoginAccount, Logout, \
    ContactView

app_name = 'backend'

urlpatterns = [
    path('partner/update/', PartnerUpdate.as_view(), name='partner-update'),
    path('user/register/', RegisterAccount.as_view(), name='user-register'),
    path('confirm/email/', ConfirmAccount.as_view(), name='confirm-email'),
    path('login/account/', LoginAccount.as_view(), name='login-account'),
    path('account/info/', AccountDetails.as_view(), name='account-info'),
    path('logout/', Logout.as_view(), name='logout'),
    path('user/contact/', ContactView.as_view(), name='contact')
]
