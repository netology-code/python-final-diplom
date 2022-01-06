from rest_framework import serializers
from products.models import ProductInfo
from orders.models import Order


class ProductInfoSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True, source='product')
    name = serializers.SlugRelatedField(read_only=True, slug_field='name', source='product')

    class Meta:
        model = ProductInfo
        fields = ['id', 'name', 'quantity', 'price']


class OrderInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status']


class OrderItemsSerializer(OrderInfoSerializer):
    items = ProductInfoSerializer(many=True, allow_null=True, source='products')
    # total = serializers.IntegerField()

    class Meta(OrderInfoSerializer.Meta):
        fields = OrderInfoSerializer.Meta.fields + ['items']
