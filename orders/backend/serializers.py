from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

from backend.models import Category, Contact, Order, OrderItem, ProductInfo, Shop, User


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }


class ImageSerializers(serializers.Serializer):
    image = serializers.ImageField()

    def validate_image(self, value):
        height, width = value.image.size
        if height + width > 2000:
            raise serializers.ValidationError('Большой размер картинки')
        return value


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)
    image = VersatileImageFieldSerializer(read_only=True, sizes='person_image')

    class Meta:
        model = User
        fields = ('id', 'email', 'company', 'last_name', 'first_name', 'position', 'contacts', 'type', 'image')
        read_only_fields = ('id',)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state',)
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    shops = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'shops')
        read_only_fields = ('id',)


class ProductInfoSerializer(serializers.ModelSerializer):
    shop = serializers.StringRelatedField()
    product = serializers.StringRelatedField()

    class Meta:
        model = ProductInfo
        fields = ('id', 'shop', 'product', 'external_id', 'quantity', 'price', 'price_rrc', 'model')
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)

    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact',)
        read_only_fields = ('id',)
