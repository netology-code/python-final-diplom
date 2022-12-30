from django.contrib.admin import register, ModelAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
# from django.utils.translation import ugettext_lazy as _

from .models import User, ConfirmEmailToken
from orders.models import Shop, Category, Product, \
    ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact


@register(User)
class UserAdmin(DjangoUserAdmin):
    ...


@register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(ModelAdmin):
    ...


@register(Shop)
class ShopAdmin(ModelAdmin):
    ...


@register(Category)
class CategoryAdmin(ModelAdmin):
    ...


@register(Product)
class ProductAdmin(ModelAdmin):
    ...


@register(ProductInfo)
class ProductInfoAdmin(ModelAdmin):
    ...


@register(Parameter)
class ParameterAdmin(ModelAdmin):
    ...


@register(ProductParameter)
class ProductParameterAdmin(ModelAdmin):
    ...


@register(Order)
class OrderAdmin(ModelAdmin):
    ...


@register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    ...


@register(Contact)
class ContactAdmin(ModelAdmin):
    ...
