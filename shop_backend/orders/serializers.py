from rest_framework import serializers
from orders.models import Order, OrderContent


class OrderContentSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(read_only=True, slug_field='product_id', source='product_info')
    name = serializers.SlugRelatedField(read_only=True, slug_field='name', source='product_info.product')
    price = serializers.SlugRelatedField(read_only=True, slug_field='price', source='product_info')

    class Meta:
        model = OrderContent
        fields = ['id', 'name', 'quantity', 'price']


class OrderInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status']


class OrderItemsSerializer(OrderInfoSerializer):
    items = OrderContentSerializer(many=True, allow_null=True, source='contents')
    total = serializers.ReadOnlyField()

    class Meta(OrderInfoSerializer.Meta):
        fields = OrderInfoSerializer.Meta.fields + ['total', 'items']
