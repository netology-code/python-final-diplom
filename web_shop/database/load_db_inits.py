"""Primary database inserts."""

if __name__ == "__main__":

    import yaml

    from web_shop import db
    from web_shop.database.models import *

    with open("inits.yaml", "r", encoding="utf-8") as f:
        inits = yaml.safe_load(f)

    # insert users, shops, categories
    users = [User(**user) for user in inits["users"]]
    shops = [Shop(**shop) for shop in inits["shops"]]
    delivery = [Delivery(**delivery) for delivery in inits["delivery"]]
    categories = [Category(**category) for category in inits["categories"]]
    models = (users, shops, delivery, categories)
    for model in models:
        db.session.bulk_save_objects(model)
    db.session.commit()

    # insert products
    products = [
        Product(*item)
        for item in {
            (product["model"], product["category"]) for product in inits["goods"]
        }
    ]
    db.session.bulk_save_objects(products)
    db.session.commit()

    # insert product_info
    product_infos = [
        ProductInfo(*item)
        for item in {
            (
                product["name"],
                product["model"],
                product["shop"],
                product["price"],
                product["price_rrc"],
                product["quantity"],
            )
            for product in inits["goods"]
        }
    ]
    db.session.bulk_save_objects(product_infos)
    db.session.commit()

    # insert parameters
    params = []
    for item in inits["goods"]:
        item_params = item["parameters"]
        params.extend([key for key in item_params.keys()])

    parameters = [Parameter(item) for item in set(params)]
    db.session.bulk_save_objects(parameters)
    db.session.commit()

    # insert x_product_parameters
    product_params = set()
    for item in inits["goods"]:
        product = item["model"]
        params = item["parameters"]
        for param in params:
            product_params.add(ProductParameter(product, param, params[param]))

    db.session.bulk_save_objects(product_params)
    db.session.commit()

    # fixup: reset all sequences to their max value
    for i in ("user", "shop", "category", "product", "product_info", "parameter"):
        db.engine.execute(
            f"SELECT setval('{i}_id_seq', (SELECT max(id) FROM public.{i}));"
        )

    print("Initial inserts done.")
