"""Testing module."""

import pytest
from web_shop.hello import hello


@pytest.mark.parametrize(("name", "result"), [("world", "Hello world"), ("serge", "Hello serge")])
def test_hello(name, result):
    """Test function.

    :param name string
    :param result string
    :return assertion
    """
    assert hello(name) == result
