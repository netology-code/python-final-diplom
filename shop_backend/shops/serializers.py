from rest_framework import serializers
from .models import Shop
from categories.models import Category
from products.models import Product, ProductInfo, Parameter, ParameterValue
from rest_framework.exceptions import ValidationError
import yaml


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
                        'Could not parse price list. Error: price list does not contain shop, categories or goods.')
                return price_list
            except yaml.YAMLError as yaml_load_exception:
                yaml_load_error = yaml_load_exception.__dict__.get('problem')
                raise ValidationError(f'Could not load price list. Error: {yaml_load_error}' if yaml_load_error
                                      else 'Unknown error.')
    except FileNotFoundError:
        raise ValidationError(f"Could not load price list. File '{price_list_filepath}' does not exist.")


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['filename']

    def create(self, validated_data):
        price_list = price_list_to_yaml(validated_data.get('filename'))
        print(price_list)

        # Creating new shop from price list yaml file content
        new_shop, _ = Shop.objects.get_or_create(
            name=price_list.get('shop'),
            defaults={
                'url': validated_data.get('url'),
                'filename': validated_data.get('filename')
            }
        )

        # Creating new categories from price list yaml file content
        for category in price_list.get('categories'):
            new_category, _ = Category.objects.update_or_create(
                id=category.get('id'),
                defaults={'name': category.get('name')}
            )
            new_category.shops.add(new_shop.id)
            new_category.save()

        # Creating new products from price list yaml file content
        for product in price_list.get('goods'):
            new_product_category = Category.objects.get(id=product.get('category'))
            new_product, _ = Product.objects.update_or_create(
                id=product.get('id'),
                defaults={
                    'name': product.get('name'),
                    'category': new_product_category
                }
            )

            ProductInfo.objects.update_or_create(
                shop_id=new_shop.id,
                product_id=new_product.id,
                defaults={
                    'quantity': product.get('quantity'),
                    'price': product.get('price'),
                    'price_rrc': product.get('price_rrc')
                }
            )

            # Creating new parameters from price list yaml file content
            for parameter, value in product['parameters'].items():
                new_parameter, _ = Parameter.objects.get_or_create(
                    name=parameter,
                    defaults={
                        'name': parameter
                    }
                )

                ParameterValue.objects.update_or_create(
                    product_id=new_product.id,
                    parameter_id=new_parameter.id,
                    defaults={
                        'value': value
                    }
                )

        return validated_data

    def validate(self, data):
        price_list_filename = data.get('filename')
        if not price_list_filename:
            raise ValidationError('Please provide a path to your price list file.')

        return data
