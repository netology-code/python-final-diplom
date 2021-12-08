from django.contrib import admin
from .models import Category


class ShopCategoryInline(admin.TabularInline):
    model = Category.shops.through
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ShopCategoryInline]
    extra = 1
