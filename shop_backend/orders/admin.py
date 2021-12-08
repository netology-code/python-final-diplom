from django.contrib import admin
from .models import Order


class OrderContentInline(admin.TabularInline):
    model = Order.products.through
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderContentInline]
    extra = 1
