from rest_framework import serializers
from .utils import price_list_to_yaml
from .models import Shop
from rest_framework.exceptions import ValidationError
from categories.models import Category
from products.models import Product, ProductInfo, Parameter, ParameterValue
from orders.serializers import OrderSerializer


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'is_closed']
        read_only_fields = ['id', 'name']


class ShopImportSerializer(ShopSerializer):
    class Meta(ShopSerializer.Meta):
        fields = ShopSerializer.Meta.fields + ['filename']

    def create(self, validated_data):
        price_list = price_list_to_yaml(validated_data.get('filename'))

        # Creating new shop from price list yaml file content
        new_shop, is_new_shop_created = Shop.objects.get_or_create(
            name=price_list.get('shop'),
            defaults={
                'user': self.context.get('request').user,
                'filename': validated_data.get('filename')
            }
        )
        if not is_new_shop_created:
            raise ValidationError({'name': ['Shop with this name already exists.']})

        # Creating new categories from price list yaml file content
        for category in price_list.get('categories'):
            new_category, _ = Category.objects.get_or_create(
                id=category.get('id'),
                defaults={'name': category.get('name')}
            )
            new_category.shops.add(new_shop.id)

        # Creating new products from price list yaml file content
        for product in price_list.get('goods'):
            new_product_category = Category.objects.get(id=product.get('category'))
            new_product, _ = Product.objects.get_or_create(
                id=product.get('id'),
                defaults={
                    'name': product.get('name'),
                    'category': new_product_category
                }
            )

            new_product_info = ProductInfo(
                shop_id=new_shop.id,
                product_id=new_product.id,
                quantity=product.get('quantity'),
                price=product.get('price'),
                price_rrc=product.get('price_rrc')
            )
            new_product_info.save()

            # Creating new parameters from price list yaml file content
            for parameter, value in product['parameters'].items():
                new_parameter, _ = Parameter.objects.get_or_create(
                    name=parameter
                )

                ParameterValue.objects.get_or_create(
                    product_id=new_product.id,
                    parameter_id=new_parameter.id,
                    defaults={'value': value}
                )

        return new_shop


class ShopStateSerializer(ShopSerializer):
    pass


class ShopOrderSerializer(ShopSerializer):
    orders = OrderSerializer(many=True, allow_null=True)

    class Meta(ShopSerializer.Meta):
        fields = ShopSerializer.Meta.fields + ['orders']
