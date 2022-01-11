from rest_framework import serializers
from .utils import price_list_to_yaml
from .models import Shop
from rest_framework.exceptions import ValidationError
from categories.models import Category, ShopCategory
from products.models import Product, ProductInfo, Parameter, ParameterValue
from django.db import transaction
from orders.serializers import BasketSerializer


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']


class ShopImportSerializer(ShopSerializer):
    class Meta(ShopSerializer.Meta):
        fields = ShopSerializer.Meta.fields + ['filename']

    def create(self, validated_data):
        price_list = price_list_to_yaml(validated_data.get('filename'))

        # Creating new shop from price list yaml file content
        with transaction.atomic():
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
                    name=category.get('name'),

                )

                new_shop_category = ShopCategory(
                    shop_id=new_shop.id,
                    category_id=new_category.id,
                    internal_category_id=category.get('id')
                )
                new_shop_category.save()

            # Creating new products from price list yaml file content
            for product in price_list.get('goods'):
                new_product_category = ShopCategory.objects.get(internal_category_id=product.get('category'))
                new_product, _ = Product.objects.get_or_create(
                    name=product.get('name'),
                    defaults={
                        'category': new_product_category.category
                    }
                )

                new_product_info = ProductInfo(
                    shop_id=new_shop.id,
                    product_id=new_product.id,
                    internal_product_id=product.get('id'),
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
    class Meta(ShopSerializer.Meta):
        fields = ShopSerializer.Meta.fields + ['is_closed']
        write_only_field = ['is_closed']


class ShopOrderSerializer(ShopSerializer):
    orders = BasketSerializer(many=True, allow_null=True)

    class Meta(ShopSerializer.Meta):
        fields = ShopSerializer.Meta.fields + ['orders']
