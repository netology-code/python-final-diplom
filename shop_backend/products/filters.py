from django_filters import rest_framework as filters
from .models import ProductInfo


class ShopCategoryFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='product__category')

    class Meta:
        model = ProductInfo
        fields = ['shop', 'category']
