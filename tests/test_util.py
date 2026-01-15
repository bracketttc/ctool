# pylint: disable=missing-module-docstring,missing-function-docstring

import pytest
from ctool import util


@pytest.mark.parametrize("path,expected", [])
def test_is_binary_dir(path, expected):
    assert util.is_binary_dir(path) == expected


def test_find_binary_dir():
    pass


def test_find_source_dir():
    pass


def test_read_cache():
    pass


def test_get_cache_value():
    pass
