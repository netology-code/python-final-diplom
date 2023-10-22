from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html

from backend.forms import ShopImportForm
from backend.models import (Category, ConfirmEmailToken, Contact, Order, OrderItem, Parameter, Product, ProductInfo,
                            ProductParameter, Shop, ShopImport, User)
from backend.tasks import do_import


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'position')}),
        ('Photo', {'fields': ('image', 'image_tag',)}),
        ('Permissions', {'fields': (
            'type',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',)}
         ),
        (
            'Person Info', {'fields': (
                'first_name', 'last_name', 'company', 'position', 'type', 'image',
            )}
        ),
    )

    list_display = ('id', 'image_tag', 'email', 'first_name', 'last_name', 'company', 'type',
                    'is_staff', 'is_active', 'is_superuser')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups',)
    search_fields = ("email", 'last_name',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            new_image = obj.image.thumbnail['100x100']
            return format_html(
                f'<img src="{new_image.url}">'
            )
        return '-'

    image_tag.short_description = 'Profile picture'


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'state',)
    list_filter = ('state',)
    search_fields = ('name',)

    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('yml-upload/', self.yml_upload, name='yml-upload'))
        return urls

    def yml_upload(self, request):
        if request.method == 'POST':
            type_user = User.objects.get(id=request.POST['user']).type
            if type_user != 'shop':
                messages.error(request, 'Только для магазинов')
                return HttpResponseRedirect(reverse('admin:yml-upload'))
            form = ShopImportForm(request.POST)
            if form.is_valid():
                form.save()
                data = form.data
                status = do_import(user_id=data['user'], url=data['yml_url'])
                if status:
                    url = reverse('admin:index')
                    messages.success(request, 'Файл успешно импортирован')
                    return HttpResponseRedirect(url)
                messages.error(request, 'Ошибка! Некорректная ссылка')
                return HttpResponseRedirect(reverse('admin:yml-upload'))
        form = ShopImportForm()
        return render(request, 'admin/yml_import_page.html', {'form': form})


@admin.register(ShopImport)
class ShopImportAdmin(admin.ModelAdmin):
    list_display = ('yml_url', 'date_added')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category',)
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('product', 'external_id', 'shop', 'quantity', 'price', 'price_rrc', 'model', 'image_tag')
    list_filter = ('price', 'price_rrc', 'shop',)

    def image_tag(self, obj):
        if obj.photo:
            new_photo = obj.photo.thumbnail['150x150']
            return format_html(
                f'<img src="{new_photo.url}">'
            )
        return '-'

    image_tag.short_description = 'Profile picture'


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('product_info', 'parameter', 'value',)
    list_filter = ('product_info',)
    fieldsets = (
        (None, {
            'fields': (
                'product_info',
            ),
        }),
        ('Parameter', {
            'fields': (('parameter', 'value'),)
        })
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'state', 'contact', 'dt',)
    list_filter = ('state', 'user',)
    readonly_fields = ('dt',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_info', 'quantity',)
    list_filter = ('quantity',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'city', 'street', 'house',)
    list_filter = ('user', 'phone', 'city',)
    fieldsets = [
        ('Main info', {
            'fields': (
                'user', 'phone', 'city', 'street', 'house',
            ),
        }),
        ('Additional info', {
            'fields': (
                'structure', 'building', 'apartment',
            )
        }
         )
    ]
    search_fields = ('city',)


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at',)
