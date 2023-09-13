from django.urls import path

from backend.views import PartnerUpdate

app_name = 'backend'

urlpatterns = [
    path('partner/update/', PartnerUpdate.as_view(), name='partner-update'),
]
