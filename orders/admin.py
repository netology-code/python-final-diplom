from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
# from django.utils.translation import gettext_lazy as _
# from django.contrib.auth import get_user_model

from .forms import UserAdminChangeForm, UserAdminCreationForm
from .models import ConfirmEmailToken, User
from orders.models import Category, Contact, Order, OrderItem, \
    Parameter, Product, ProductInfo, ProductParameter, Shop


class UserCompanyInline:
    pass


@register(User)
class UserAdmin(DjangoUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    search_fields = ['email', 'first_name', 'last_name',
                     'is_staff', 'is_active']
    list_display = ['email', 'is_staff', 'is_active',
                    'user_type', 'company', 'position']
    list_filter = ['is_staff', 'is_active']
    add_fieldsets = (
        (None, {
            'fields': ('first_name',
                       'last_name',
                       'email',
                       'password1',
                       'password2',
                       'user_type',
                       'company',
                       'position')},
         ),
    )
    ordering = ('email',)
    filter_horizontal = ()


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
