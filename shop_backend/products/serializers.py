from rest_framework import serializers
from .models import ProductInfo


class ProductInfoSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(read_only=True, slug_field='name', source='product')
    category = serializers.SlugRelatedField(read_only=True, slug_field='name', source='product.category')

    class Meta:
        model = ProductInfo
        fields = ['name', 'category', 'price', 'quantity']
