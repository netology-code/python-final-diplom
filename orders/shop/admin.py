from django.contrib import admin
from .models import Shop, Category, Parameter, Product, ProductParameter, ProductInfo, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 1


class ProductInfoInline(admin.TabularInline):
    model = ProductInfo
    extra = 1


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    model = Shop
    fieldsets = (
        (None, {'fields': ('name', 'state')}),
        ('Additional info', {'fields': ('url', 'user'),
                             'classes': ('collapse',)}),
    )
    list_display = ('name', 'state', 'url')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    model = Product
    inlines = [ProductInfoInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    model = Order
    fields = ('user', 'status', 'contact')
    list_display = ('user', 'dt', 'status')
    ordering = ('-dt',)
    inlines = [OrderItemInline]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    inlines = [ProductParameterInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass