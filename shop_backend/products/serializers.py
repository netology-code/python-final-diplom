from rest_framework import serializers
from .models import ProductInfo


class ProductInfoSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(read_only=True, slug_field='id', source='product')
    name = serializers.SlugRelatedField(read_only=True, slug_field='name', source='product')
    shop = serializers.SlugRelatedField(read_only=True, slug_field='name')
    category = serializers.SlugRelatedField(read_only=True, slug_field='name', source='product.category')

    class Meta:
        model = ProductInfo
        fields = ['id', 'name', 'price', 'shop', 'category']
