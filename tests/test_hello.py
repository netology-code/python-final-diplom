"""Testing module."""

import pytest
from web_shop.hello import hello


@pytest.mark.parametrize(("name", "result"), [("world", "Hello world"), ("Sergey", "Hello Sergey")])
def test_hello(name, result):
    """Test function.

    :param name string
    :param result string
    :return assertion
    """
    assert hello(name) == result


if __name__ == "__main__":
    pytest.main()
