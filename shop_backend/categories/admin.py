from django.contrib import admin
from .models import Category, ShopCategory


class ShopCategoryInline(admin.TabularInline):
    model = ShopCategory
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ShopCategoryInline]
    extra = 1
