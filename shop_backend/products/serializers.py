from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SlugRelatedField(read_only=True, slug_field='product_price', source='prices')

    class Meta:
        model = Product
        fields = ['id', 'name', 'price']
