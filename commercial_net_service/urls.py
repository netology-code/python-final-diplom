"""commercial_net_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from orders.views import PartnerUpdate, LoginAccount, RegisterAccount, ProductsList, ShopView, ProductsView, \
    SingleProductView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('token/', obtain_auth_token),
    path('user/login', LoginAccount.as_view(), name='user-login'),
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path('products/list', ProductsList.as_view(), name='products-list'),
    path('products/view', ProductsView.as_view(), name='products-view'),
    path('product/view_by_id', SingleProductView.as_view(), name='product-cart-view'),
    path('shop/list', ShopView.as_view(), name='shop-list'),

]
