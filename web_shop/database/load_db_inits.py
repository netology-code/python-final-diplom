"""Primary database inserts."""

if __name__ == "__main__":

    import yaml

    from web_shop import db
    from web_shop.database.models import *

    with open("inits.yaml", "r", encoding="utf-8") as f:
        inits = yaml.safe_load(f)

    users = [User(**user) for user in inits["users"]]
    shops = [Shop(**shop) for shop in inits["shops"]]
    categories = [Category(**category) for category in inits["categories"]]

    models = (users, shops, categories)

    for model in models:
        db.session.bulk_save_objects(model)
    db.session.commit()

    products = [
        Product(*item)
        for item in {
            (product["model"], product["category"]) for product in inits["goods"]
        }
    ]
    db.session.bulk_save_objects(products)
    db.session.commit()

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

    params = []
    for item in inits["goods"]:
        item_params = item["parameters"]
        params.extend([key for key in item_params.keys()])

    parameters = [Parameter(item) for item in set(params)]
    db.session.bulk_save_objects(parameters)
    db.session.commit()

    p_params = set()
    for item in inits["goods"]:
        shop = item["shop"]
        product = item["name"]
        params = item["parameters"]
        for param in params:
            p_params.add((product, param, params[param]))

    product_params = [ProductParameter(*item) for item in p_params]
    db.session.bulk_save_objects(product_params)
    db.session.commit()

    print("Initial inserts done.")
