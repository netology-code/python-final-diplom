from .models import Shop
from categories.models import Category
from products.models import Product, ProductInfo, Parameter, ParameterValue
from rest_framework.exceptions import ValidationError
import yaml
from rest_framework import serializers
from orders.serializers import OrderInfoSerializer


def is_price_list_valid(price_list: dict) -> bool:
    match price_list:
        case {
            'shop': shop,
            'categories': categories,
            'goods': goods
        } if (isinstance(shop, str) and isinstance(categories, list) and isinstance(goods, list)):
            return True
        case _:
            return False


def price_list_to_yaml(price_list_filepath: str) -> dict:
    try:
        with open(price_list_filepath, mode='r', encoding='utf-8') as price_list_file:
            try:
                price_list = yaml.safe_load(price_list_file)
                if not price_list:
                    raise ValidationError(f"Could not parse price list. Error: file '{price_list_filepath} is empty.")
                if not is_price_list_valid(price_list):
                    raise ValidationError(
                        'Could not parse price list. Error: price list is of invalid format.')
                return price_list
            except yaml.YAMLError as yaml_load_exception:
                yaml_load_error = yaml_load_exception.__dict__.get('problem')
                raise ValidationError(f'Could not load price list. Error: {yaml_load_error}' if yaml_load_error
                                      else 'Unknown error.')
    except FileNotFoundError:
        raise ValidationError(f"Could not load price list. Error: file '{price_list_filepath}' does not exist.")


class ShopImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['filename']

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


class ShopStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'is_closed']
        read_only_fields = ['id', 'name']


class ShopOrderSerializer(serializers.ModelSerializer):
    orders = OrderInfoSerializer(many=True, allow_null=True)

    class Meta:
        model = Shop
        fields = ['id', 'name', 'orders']
