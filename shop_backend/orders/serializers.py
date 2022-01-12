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
        basket_positions = validated_data.pop('contents')
        if not basket_positions:
            raise ValidationError({'results': ['You need to add at least one position to basket.']})

        for basket_position in basket_positions:
            basket_position_id = basket_position.get('product_info').get('id')
            basket_position_quantity = basket_position.get('quantity')
            position_in_stock = ProductInfo.objects.get(id=basket_position_id)

            if basket_position.get('quantity') > position_in_stock.quantity:
                raise ValidationError(
                    {'results': [
                        f'Cannot add {basket_position_quantity} items of position {basket_position_id}. '
                        f'Only {position_in_stock.quantity} is in stock.']})

            OrderContent.objects.update_or_create(
                order=instance,
                product_info=position_in_stock,
                defaults={'quantity': basket_position_quantity}
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
