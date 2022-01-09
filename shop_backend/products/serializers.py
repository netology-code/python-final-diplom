from rest_framework import serializers
from .models import ProductInfo, ParameterValue


class ParameterSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(read_only=True, slug_field='name', source='parameter')

    class Meta:
        model = ParameterValue
        fields = ['name', 'value']


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(read_only=True, slug_field='id', source='product')
    name = serializers.SlugRelatedField(read_only=True, slug_field='name', source='product')
    shop = serializers.SlugRelatedField(read_only=True, slug_field='name')
    category = serializers.SlugRelatedField(read_only=True, slug_field='name', source='product.category')
    parameters = ParameterSerializer(many=True, allow_null=True, source='product.parameters')

    class Meta:
        model = ProductInfo
        fields = ['id', 'name', 'price', 'shop', 'category', 'parameters']
