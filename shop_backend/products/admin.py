from django.contrib import admin
from .models import Product, Parameter


class ProductValueInline(admin.TabularInline):
    model = Parameter.products.through
    extra = 1


class ProductInfoInline(admin.TabularInline):
    model = Product.shops.through
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductValueInline, ProductInfoInline]
    extra = 1


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    inlines = [ProductValueInline]
    extra = 1
