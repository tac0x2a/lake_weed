
import pytest
from lakeweed import flatten


def test_flatten():
    src = {
        "hoge": 42
    }
    expected = {
        "hoge": 42
    }
    res = flatten.flatten(src)
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
        "fuga__a": 43,
        "fuga__b": 44,
    }
    res = flatten.flatten(src)
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
        "fuga.a": 43,
        "fuga.b": 44,
    }
    res = flatten.flatten(src, delimiter=".")
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
        "fuga__a": 43,
        "fuga__b": 44,
        "fuga__c": [1, 2, 3],
        "piyo": [{"a": 42, "b": 43}]
    }
    res = flatten.flatten(src)
    assert expected == res


if __name__ == '__main__':
    pytest.main(['-v', __file__])
