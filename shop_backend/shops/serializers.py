from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from .models import Shop
from categories.models import Category
from products.models import Product, ProductInfo, Parameter, ParameterValue
from rest_framework.exceptions import ValidationError
import yaml
from rest_framework import status
import django.db.utils


def price_list_to_yaml(price_list_filepath: str) -> dict | str:
    try:
        with open(price_list_filepath, encoding='utf-8') as price_list_file:
            try:
                return yaml.safe_load(price_list_file)
            except yaml.YAMLError as yaml_load_exception:
                yaml_load_error = yaml_load_exception.__dict__.get('problem')
                raise ValidationError(f'Could not load price list. Error: {yaml_load_error}' if yaml_load_error
                                      else 'Unknown error.')
    except FileNotFoundError:
        raise ValidationError(f'Could not load price list. File {price_list_filepath} does not exist.')


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['filename']

    def create(self, validated_data):
        price_list = price_list_to_yaml(validated_data.get('filename'))

        # Creating new shop from price list yaml file content
        try:
            new_shop, _ = Shop.objects.update_or_create(
                name=price_list.get('shop'),
                defaults={
                    'url': validated_data.get('url'),
                    'filename': validated_data.get('filename')
                }
            )
        except django.db.utils.IntegrityError:
            return Response(
                {'Error': 'Price list does not contain any shops.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Creating new categories from price list yaml file content
        for category in price_list.get('categories'):
            try:
                new_category, _ = Category.objects.update_or_create(
                    id=category.get('id'),
                    defaults={'name': category.get('name')}
                )
                new_category.shops.add(new_shop.id)
                new_category.save()
            except django.db.utils.IntegrityError:
                return Response(
                    {'Error': 'Price list does not contain any categories.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Creating new products from price list yaml file content
        for product in price_list.get('goods'):
            try:
                new_product_category = Category.objects.get(id=product.get('category'))
                new_product, _ = Product.objects.update_or_create(
                    id=product.get('id'),
                    defaults={
                        'name': product.get('name'),
                        'category': new_product_category
                    }
                )
            except django.db.utils.IntegrityError:
                return Response(
                    {'Error': 'Price list does not contain any products.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                ProductInfo.objects.update_or_create(
                    shop_id=new_shop.id,
                    product_id=new_product.id,
                    defaults={
                        'quantity': product.get('quantity'),
                        'price': product.get('price'),
                        'price_rrc': product.get('price_rrc')
                    }
                )
            except django.db.utils.IntegrityError:
                return Response(
                    {'Error': 'Price list does not contain any info on product quantity and price.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Creating new parameters from price list yaml file content
            for parameter, value in product['parameters'].items():
                try:
                    new_parameter, _ = Parameter.objects.get_or_create(
                        name=parameter,
                        defaults={
                            'name': parameter
                        }
                    )
                except django.db.utils.IntegrityError:
                    return Response(
                        {'Error': 'Price list does not contain any parameters.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                try:
                    ParameterValue.objects.update_or_create(
                        product_id=new_product.id,
                        parameter_id=new_parameter.id,
                        defaults={
                            'value': value
                        }
                    )
                except django.db.utils.IntegrityError:
                    return Response(
                        {'Error': 'Price list does not contain any info on parameter value.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        return Response(validated_data, status=status.HTTP_201_CREATED)

    def validate(self, data):
        price_list_filename = data.get('filename')
        if not price_list_filename:
            raise ValidationError('Please provide a path to your price list file.')

        return data
