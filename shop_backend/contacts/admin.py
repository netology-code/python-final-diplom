from django.contrib import admin
from .models import UserInfo, Contact
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    extra = 1


class UserInfoInline(admin.StackedInline):
    model = UserInfo


class UserAdmin(BaseUserAdmin):
    inlines = [UserInfoInline]
    extra = 1


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
