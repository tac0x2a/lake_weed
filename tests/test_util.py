
import pytest
from datetime import datetime, timezone, timedelta

from lakeweed import util
from lakeweed.time_parser import DateTimeWithNS


def test_flatten():
    src = {
        "hoge": 42
    }
    expected = {
        "hoge": 42
    }
    res = util.flatten(src)
    assert expected == res


def test_flatten_nested():
    src = {
        "hoge": 42,
        "fuga": {
            "a": 43,
            "b": 44,
        }
    }
    expected = {
        "hoge": 42,
        "fuga.a": 43,
        "fuga.b": 44,
    }
    res = util.flatten(src)
    assert expected == res


def test_flatten_nested_specified_delimiter():
    src = {
        "hoge": 42,
        "fuga": {
            "a": 43,
            "b": 44,
        }
    }
    expected = {
        "hoge": 42,
        "fuga__a": 43,
        "fuga__b": 44,
    }
    res = util.flatten(src, delimiter="__")
    assert expected == res


def test_flatten_array():
    src = {
        "hoge": 42,
        "fuga": {
            "a": 43,
            "b": 44,
            "c": [1, 2, 3]
        },
        "piyo": [{"a": 42, "b": 43}]
    }
    expected = {
        "hoge": 42,
        "fuga.a": 43,
        "fuga.b": 44,
        "fuga.c": [1, 2, 3],
        "piyo": [{"a": 42, "b": 43}]
    }
    res = util.flatten(src)
    assert expected == res


if __name__ == '__main__':
    pytest.main(['-v', __file__])


def test_specified_int_int():
    src = 42
    specified = "int"
    expected = 42
    res = util.__cast_specified(src, specified)
    assert expected == res
    assert type(expected) == type(res)


def test_specified_float_float():
    src = -42.2
    specified = "float"
    expected = -42.2
    res = util.__cast_specified(src, specified)
    assert expected == res
    assert type(expected) == type(res)


def test_specified_int_float():
    src = 42
    specified = "float"
    expected = 42.0
    res = util.__cast_specified(src, specified)
    assert expected == res
    assert type(expected) == type(res)


def test_specified_float_int():
    src = 42.0
    specified = "int"
    expected = 42
    res = util.__cast_specified(src, specified)
    assert expected == res
    assert type(expected) == type(res)


def test_specified_int_string():
    src = 42
    specified = "string"
    expected = "42"
    res = util.__cast_specified(src, specified)
    assert expected == res
    assert type(expected) == type(res)


def test_specified_float_string():
    src = 42.195
    specified = "string"
    expected = "42.195"
    res = util.__cast_specified(src, specified)
    assert expected == res
    assert type(expected) == type(res)


def test_specified_string_float():
    src = "42.195"
    specified = "double"  # double and decimal are available instead of float
    expected = 42.195
    res = util.__cast_specified(src, specified)
    assert expected == res
    assert type(expected) == type(res)


def test_specified_raise_if_not_valid_type():
    src = "42.195"
    specified = "INVALID"  # double and decimal are available instead of float
    with pytest.raises(TypeError):
        util.__cast_specified(src, specified)
