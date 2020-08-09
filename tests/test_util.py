
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


def test_basic_data_types():
    src = [
        42,
        42.195,
        True,
        "2020-08-09 11:04:00",
        "Hello, LakeWeed",
        [1, 2.2, 3.3],
        [1.1, 2, 3],
        ["2020-08-09 11:04:00", "2020-08-09 11:05:00", "2020-08-09 11:06:00"],
        ["2020-08-09 11:04:00", "hoge"],
        [[1, 2, 3], [], ["hoge"]],
    ]
    expected = [
        "Float",
        "Float",
        "Bool",
        "DateTime",
        "String",
        "Array(Float)",
        "Array(Float)",
        "Array(DateTime)",
        "Array(DateTime)",
        "Array(Array(Float))"
    ]
    res = util.data_types(src)
    assert expected == res
