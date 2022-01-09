from rest_framework import serializers
from orders.models import Order, OrderContent
from products.serializers import ProductInfoSerializer
from rest_framework.exceptions import ValidationError


class OrderContentSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(read_only=True, slug_field='product_id', source='product_info')
    name = serializers.SlugRelatedField(read_only=True, slug_field='name', source='product_info.product')
    price = serializers.SlugRelatedField(read_only=True, slug_field='price', source='product_info')

    class Meta:
        model = OrderContent
        fields = ['id', 'name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    products = ProductInfoSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status', 'products']

    def create(self, validated_data):
        new_order = Order(
            user=self.context.get('request').user
        )
        new_order.save()

        return new_order

    def validate(self, data):
        if not data.get('products'):
            raise ValidationError({'results': ['Please add at least one product to basket.']})

        return data


class OrderItemsSerializer(OrderSerializer):
    items = OrderContentSerializer(many=True, allow_null=True, source='contents')
    total = serializers.ReadOnlyField()

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ['total', 'items']
