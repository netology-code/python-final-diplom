def is_price_list_categories_valid(categories: list) -> bool | str:
    for index, category in enumerate(categories):
        if 'id' not in category:
            return f'Field "id" not found in category #{index + 1}.'
        elif not isinstance(category.get('id'), int):
            return f'Field "id" of category #{index + 1} is not a number.'
        elif 'name' not in category:
            return f'Field "name" not found in category #{index + 1}.'
        elif not isinstance(category.get('name'), str):
            return f'Field "name" of category #{index + 1} is not a string.'
        else:
            return True


def is_price_list_goods_valid(goods: list) -> bool | str:
    for index, good in enumerate(goods):
        if 'id' not in good:
            return f'Field "id" not found in product #{index + 1}.'
        elif not isinstance(good.get('id'), int):
            return f'Field "id" of product #{index + 1} is not a number.'
        elif 'category' not in good:
            return f'Field "category" not found in product #{index + 1}.'
        elif not isinstance(good.get('category'), int):
            return f'Field "category" of product #{index + 1} is not a number.'
        elif 'model' not in good:
            return f'Field "model" not found in product #{index + 1}.'
        elif not isinstance(good.get('model'), str):
            return f'Field "model" of product #{index + 1} is not a string.'
        elif 'name' not in good:
            return f'Field "name" not found in product #{index + 1}.'
        elif not isinstance(good.get('name'), str):
            return f'Field "name" of product #{index + 1} is not a string.'
        elif 'price' not in good:
            return f'Field "price" not found in product #{index + 1}.'
        elif not isinstance(good.get('price'), int):
            return f'Field "price" of product #{index + 1} is not a number.'
        elif 'price_rrc' not in good:
            return f'Field "price_rrc" not found in product #{index + 1}.'
        elif not isinstance(good.get('price_rrc'), int):
            return f'Field "price_rrc" of product #{index + 1} is not a number.'
        elif 'quantity' not in good:
            return f'Field "quantity" not found in product #{index + 1}.'
        elif not isinstance(good.get('quantity'), int):
            return f'Field "quantity" of product #{index + 1} is not a number.'
        elif 'parameters' not in good:
            return f'Field "parameters" not found in product #{index + 1}.'
        elif not good.get('parameters'):
            return f'Field "parameters" not found in product #{index + 1}.'
        else:
            return True