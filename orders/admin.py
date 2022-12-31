from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
# from django.utils.translation import ugettext_lazy as _

from .models import ConfirmEmailToken, User
from orders.models import Category, Contact, Order, OrderItem, \
    Parameter, Product, ProductInfo, ProductParameter, Shop


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
