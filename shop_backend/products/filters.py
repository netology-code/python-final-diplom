from django_filters import rest_framework as filters
from .models import Product
from shops.models import Shop


class ProductShopCategoryFilter(filters.FilterSet):
    shop = filters.ModelMultipleChoiceFilter(field_name='shops', queryset=Shop.objects.all())

    class Meta:
        model = Product
        fields = ['shop', 'category']
