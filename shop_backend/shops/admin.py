from django.contrib import admin
from .models import Shop
from categories.admin import ShopCategoryInline
from products.admin import ProductInfoInline


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    inlines = [ShopCategoryInline, ProductInfoInline]
    extra = 1
