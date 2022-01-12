from rest_framework import serializers
from orders.models import Order, OrderContent
from products.models import ProductInfo
from rest_framework.exceptions import ValidationError


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'created_at']


class BasketPositionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product_info.id')

    class Meta:
        model = OrderContent
        fields = ['id', 'quantity']


class BasketSerializer(serializers.ModelSerializer):
    positions = BasketPositionSerializer(many=True, source='contents')

    class Meta:
        model = Order
        fields = ['id', 'positions']
        extra_kwargs = {field: {'required': True} for field in fields}

    def update(self, instance, validated_data):
        positions = validated_data.pop('contents')
        if not positions:
            raise ValidationError({'results': ['You need to add at least one position to basket.']})

        for position in positions:
            OrderContent.objects.update_or_create(
                order=instance,
                product_info=ProductInfo.objects.get(id=position.get('product_info').get('id')),
                defaults={'quantity': position.get('quantity')}
            )

        return instance


class OrderContentSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(read_only=True, slug_field='product_id', source='product_info')
    name = serializers.SlugRelatedField(read_only=True, slug_field='name', source='product_info.product')
    price = serializers.SlugRelatedField(read_only=True, slug_field='price', source='product_info')

    class Meta:
        model = OrderContent
        fields = ['id', 'name', 'quantity', 'price']


class OrderItemsSerializer(BasketSerializer):
    items = OrderContentSerializer(many=True, allow_null=True, source='contents')
    total = serializers.ReadOnlyField()

    class Meta(BasketSerializer.Meta):
        fields = BasketSerializer.Meta.fields + ['total', 'items']
