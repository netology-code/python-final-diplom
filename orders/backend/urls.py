from django.urls import path

from backend.views import PartnerUpdate, RegisterAccount

app_name = 'backend'

urlpatterns = [
    path('partner/update/', PartnerUpdate.as_view(), name='partner-update'),
    path('user/register/', RegisterAccount.as_view(), name='user-register')
]
