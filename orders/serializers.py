from rest_framework.serializers import ModelSerializer, IntegerField
from rest_framework.relations import StringRelatedField

from orders.models import User, Contact, Product, Shop, Category, \
    ProductInfo, ProductParameter, Order, OrderItem


class ContactSerializer(ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'user_id', 'city', 'street', 'house',
                  'structure', 'building', 'apartment',
                  'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True},
        }


class UserSerializer(ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'company',
                  'position', 'contacts', 'user_type')
        read_only_fields = ('id',)


class ProductSerializer(ModelSerializer):
    category = StringRelatedField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'category')
        extra_kwargs = {'name': {'required': False}}


class ProductParameterSerializer(ModelSerializer):
    parameter = StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value')


class ShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state')
        read_only_fields = ('id',)


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id')


class ProductViewSerializer(ModelSerializer):
    category = StringRelatedField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'category')
        extra_kwargs = {'name': {'required': False}}


class SingleProductViewSerializer(ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True,
                                                    many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'name', 'product', 'shop', 'quantity',
                  'price', 'price_rrc', 'product_parameters')
        read_only_fields = ('id',)


class OrderItemSerializer(ModelSerializer):
    product_info = SingleProductViewSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order')
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True},
        }


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = SingleProductViewSerializer(read_only=True)


class OrderSerializer(ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True,
                                              many=True)

    total_sum = IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state', 'dt',
                  'total_sum', 'contact')
        read_only_fields = ('id',)
