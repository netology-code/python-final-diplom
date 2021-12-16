import yaml


def price_list_to_yaml(price_list_filepath: str) -> dict:
    try:
        with open(price_list_filepath, mode='r', encoding='utf-8') as price_list_file:
            try:
                price_list = yaml.safe_load(price_list_file)
                if not price_list:
                    pass
                # if not is_price_list_valid(price_list):
                #     pass
                return price_list
            except yaml.YAMLError as yaml_load_exception:
                yaml_load_error = yaml_load_exception.__dict__.get('problem')
                pass
    except FileNotFoundError:
        pass


pl = price_list_to_yaml('test.yaml')

#print(pl['goods'])

for good in pl['goods']:
    print(good)
    print('parameters are here?')
    print('parameters' in good)
    print('parameters are empty?')
    if good.get('parameters'):
        print('no')
    else:
        print('yes')
