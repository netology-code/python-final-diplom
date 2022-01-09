from rest_framework import serializers
from .models import ParameterValue, ProductInfo, Product


class ParameterSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(read_only=True, slug_field='name', source='parameter')

    class Meta:
        model = ParameterValue
        fields = ['name', 'value']


class ProductInfoSerializer(serializers.ModelSerializer):
    shop = serializers.SlugRelatedField(read_only=True, slug_field='name')
    category = serializers.SlugRelatedField(read_only=True, slug_field='name', source='product.category')
    # parameters = ParameterSerializer(many=True, allow_null=True, source='product.parameters')

    class Meta:
        model = ProductInfo
        fields = ['shop', 'category', 'price']


class ProductSerializer(serializers.ModelSerializer):
    available_in = ProductInfoSerializer(many=True, allow_null=True, source='infos')

    class Meta:
        model = Product
        fields = ['name', 'available_in']
