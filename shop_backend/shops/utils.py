import yaml
from rest_framework.exceptions import ValidationError


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
