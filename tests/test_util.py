
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


def test_return_traverse_datetime_parse_datetime():
    src = {
        "hello": "2018/11/14",
        "world": "2018/11/15 11:22:33.123456789",
        "hoge": "2018/13/15 11:22:33"
    }
    expected = {
        "hello": DateTimeWithNS(datetime(2018, 11, 14, 0, 0, 0, 0, timezone(timedelta(hours=0))), 0, "2018/11/14"),
        "world": DateTimeWithNS(datetime(2018, 11, 15, 11, 22, 33, 123456, timezone(timedelta(hours=0))), 123456789, "2018/11/15 11:22:33.123456789"),
        "hoge": "2018/13/15 11:22:33"
    }
    res = util.traverse_datetime_parse(src)
    assert expected == res


def test_return_traverse_datetime_parse_datetime_array():
    src = {
        "hello": ["2018/11/14", "2018/11/15 11:22:33.123456789"]
    }
    expected = {
        "hello": [
            DateTimeWithNS(datetime(2018, 11, 14, 0, 0, 0, 0, timezone(timedelta(hours=0))), 0, "2018/11/14"),
            DateTimeWithNS(datetime(2018, 11, 15, 11, 22, 33, 123456, timezone(timedelta(hours=0))), 123456789, "2018/11/15 11:22:33.123456789")
        ]
    }
    res = util.traverse_datetime_parse(src)
    assert expected == res


def test_traverse_datetime_parse_return_original_string_array_if_contains_invalid_datetime():
    src = {
        "hello": ["2018/11/14", "2018/11/15 11:22:33.123456789", "2018/13/15 11:22:33"]
    }
    expected = {
        "hello": ["2018/11/14", "2018/11/15 11:22:33.123456789", "2018/13/15 11:22:33"]
    }
    res = util.traverse_datetime_parse(src)
    assert expected == res


if __name__ == '__main__':
    pytest.main(['-v', __file__])
