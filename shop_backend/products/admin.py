from django.contrib import admin
from .models import ParameterValue, ProductInfo, Product, Parameter


class ParameterValueInline(admin.TabularInline):
    model = ParameterValue
    extra = 1


class ProductInfoInline(admin.TabularInline):
    model = ProductInfo
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ParameterValueInline, ProductInfoInline]
    extra = 1


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    inlines = [ParameterValueInline]
    extra = 1
