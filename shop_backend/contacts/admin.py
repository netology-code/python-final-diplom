from django.contrib import admin
from .models import User, Contact


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    extra = 1


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    extra = 1
