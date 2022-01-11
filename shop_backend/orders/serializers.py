from rest_framework import serializers
from orders.models import Order, OrderContent
from rest_framework.exceptions import ValidationError
from products.models import ProductInfo
from django.db import transaction


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status']


class OrderContentSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(read_only=True, slug_field='product_id', source='product_info')
    name = serializers.SlugRelatedField(read_only=True, slug_field='name', source='product_info.product')
    price = serializers.SlugRelatedField(read_only=True, slug_field='price', source='product_info')

    class Meta:
        model = OrderContent
        fields = ['id', 'name', 'quantity', 'price']


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = ['shop', 'product', 'quantity']
        extra_kwargs = {field: {'required': True} for field in fields}


class BasketSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'products']

    def create(self, validated_data):
        new_order = Order(
            user=self.context.get('request').user
        )

        products = validated_data.pop('products')
        order_contents = []
        for product in products:
            product_info = ProductInfo.objects.get(shop=product.get('shop'), product=product.get('product'))

            order_product_quantity = product.get('quantity')
            if order_product_quantity > product_info.quantity:
                raise ValidationError({'results': [
                    f'Cannot put {order_product_quantity} positions of product "{product.get("product").name}" '
                    f'to basket. Only {product_info.quantity} is in stock.']})

            order_contents.append(
                OrderContent(quantity=product.get('quantity'), order=new_order, product_info=product_info))

        with transaction.atomic():
            new_order.save()
            OrderContent.objects.bulk_create(order_contents)

        return new_order

    def validate(self, data):
        try:
            order = Order.objects.get(user=self.context['request'].user, status='basket')
        except Order.DoesNotExist:
            pass
        else:
            raise ValidationError(
                {'results': [f'Basket already exists. Id: {order.id}. Either delete it, or add products to it']})

        if not data.get('products'):
            raise ValidationError({'results': ['Please add at least one product to basket.']})

        return data


class OrderItemsSerializer(BasketSerializer):
    items = OrderContentSerializer(many=True, allow_null=True, source='contents')
    total = serializers.ReadOnlyField()

    class Meta(BasketSerializer.Meta):
        fields = BasketSerializer.Meta.fields + ['total', 'items']
