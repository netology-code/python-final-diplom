from timeit import timeit


def main_if(d):
    a = d.get('key')

    if not a:
        pass


def main_try(d):
    try:
        a = d['key']
    except KeyError as err:
        pass


print(timeit('main_if({})', globals=globals(), number=10000000))
print(timeit('main_try({})', globals=globals(), number=10000000))
