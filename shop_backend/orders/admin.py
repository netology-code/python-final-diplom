from django.contrib import admin
from .models import OrderContent, Order


class OrderContentInline(admin.TabularInline):
    model = OrderContent
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderContentInline]
    extra = 1
