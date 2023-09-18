from rest_framework import serializers

from backend.models import User, Contact, Shop, Category, ProductInfo


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'company', 'last_name', 'first_name', 'position', 'contacts')
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
        fields = ('id', 'shop', 'product', 'quantity', 'price', 'price_rrc', 'model')
        read_only_fields = ('id',)
