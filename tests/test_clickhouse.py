from datetime import datetime, timezone, timedelta

from lakeweed import clickhouse


def test_return_empty_set():
    src = "{}"
    expected = ((), (), [()])
    res = clickhouse.data_string2type_value(src)
    assert res == expected


def test_return_basic_type_and_values():
    src = """
    { "hello" : 42, "world" : 128.4, "bool" : true, "str" : "Hello,World" }
    """

    expected = (
        ("hello", "world", "bool", "str"),
        ("Float64", "Float64", "UInt8", "String"),
        [(42, 128.4, 1, "Hello,World")]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_basic_type_and_values_csv():
    src = """
    hello, world, bool, str
    42, 128.4, true, "Hello,World"
    """

    expected = (
        ("hello", "world", "bool", "str"),
        ("Float64", "Float64", "UInt8", "String"),
        [(42, 128.4, 1, "Hello,World")]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_DateTime_and_UInt32_type_if_DateTime_like_string_provided():
    src = """
    { "hello" : "2018/11/14", "world" : "2018/11/15 11:22:33.123456789", "hoge" : "2018/13/15 11:22:33"}
    """
    expected = (
        ("hello", "hello_ns", "world", "world_ns", "hoge"),
        ("DateTime", "UInt32", "DateTime", "UInt32", "String"),
        [
            (
                datetime(2018, 11, 14, 0, 0, 0, 0, timezone(timedelta(hours=0))),
                0,
                datetime(2018, 11, 15, 11, 22, 33, 123456, timezone(timedelta(hours=0))),
                123456789,
                "2018/13/15 11:22:33"
            )
        ]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res

def test_return_DateTime_and_UInt32_type_if_DateTime_like_string_provided_csv():
    src = """
    hello, world, hoge
    "2018/11/14", "2018/11/15 11:22:33.123456789", "2018/13/15 11:22:33"
    """
    expected = (
        ("hello", "hello_ns", "world", "world_ns", "hoge"),
        ("DateTime", "UInt32", "DateTime", "UInt32", "String"),
        [
            (
                datetime(2018, 11, 14, 0, 0, 0, 0, timezone(timedelta(hours=0))),
                0,
                datetime(2018, 11, 15, 11, 22, 33, 123456, timezone(timedelta(hours=0))),
                123456789,
                "2018/13/15 11:22:33"
            )
        ]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_nested_values_splited_by__():
    src = """
    { "hello" : 42, "world" : { "value" : 128.4, "bool" : true, "deep" : {"str" : "Hello,World" } } }
    """

    expected = (
        ("hello", "world__value", "world__bool", "world__deep__str"),
        ("Float64", "Float64", "UInt8", "String"),
        [(42, 128.4, 1, "Hello,World")]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_array_values():
    src = """
    { "hello" : [42, -84, 128], "world" : [128.4, -255.3], "bool" : [true, false, true, false],  "str" : ["Hello", "World", "Hoge"]}
    """

    expected = (
        ("hello", "world", "bool", "str"),
        ("Array(Float64)", "Array(Float64)", "Array(UInt8)", "Array(String)"),
        [([42, -84, 128], [128.4, -255.3], [1, 0, 1, 0], ['Hello', 'World', 'Hoge'])]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_String_array_values_if_DateTime_like_strings():
    src = """
    {"hello" : ["2018/11/14", "2018/11/15 11:22:33.123456789"]}
    """

    expected = (
        ("hello", "hello_ns"),
        ("Array(DateTime)", "Array(UInt32)"),
        [(
            [
                datetime(2018, 11, 14, 0, 0, 0, 0, timezone(timedelta(hours=0))),
                datetime(2018, 11, 15, 11, 22, 33, 123456, timezone(timedelta(hours=0)))
            ],
            [0, 123456789]
        )]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_array_under_object():
    src = """
    { "hello" : 42, "world" : { "value" : [128.4, -255.3] } }
    """

    expected = (
        ("hello", "world__value"),
        ("Float64", "Array(Float64)"),
        [(42, [128.4, -255.3])]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_string_Array_if_empyt_array():
    src = """
    { "empty" : [], "nested" : [[]]}
    """

    expected = (
        ("empty", "nested"),
        ("Array(String)", "Array(String)"),
        [([], ['[]'])]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_String_nested_array():
    src = """
    {
        "hello" : [[1.1, 2.2], [3.3, 4.4]],
        "world" : { "value" : [[1,2], [3,4]]},
        "hoge"  : [{"v": 1}, {"v": 2}]
    }
    """

    expected = (
        ("hello", "world__value", "hoge"),
        ("Array(String)", "Array(String)", "Array(String)"),
        [(
            ['[1.1, 2.2]', '[3.3, 4.4]'],
            ['[1, 2]', '[3, 4]'],
            ['{"v": 1}', '{"v": 2}']
        )]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_values_as_string_for_clickhouse_query():
    src = """
    {
      "array" : [1,2,3],
      "hello" : [[1.1, 2.2], [3.3, 4.4]],
      "world" : {"value" : [[1,2], [3,4]]},
      "hoge"  : [{"v":1}, {"v":2}],
      "dates" : ["2019/09/15 14:50:03.101 +0900", "2019/09/15 14:50:03.202 +0900"],
      "date"  : "2019/09/15 14:50:03.042042043 +0900",
      "str"   : "Hello String"
    }
    """
    expected = (
        ("array", "hello", "world__value", "hoge", "dates", "dates_ns", "date", "date_ns", "str"),
        [(
            [1, 2, 3],
            ['[1.1, 2.2]', '[3.3, 4.4]'],
            ['[1, 2]', '[3, 4]'],
            ['{"v": 1}', '{"v": 2}'],
            [
                datetime(2019, 9, 15, 14, 50, 3, 101000, timezone(timedelta(hours=9))),
                datetime(2019, 9, 15, 14, 50, 3, 202000, timezone(timedelta(hours=9))),
            ],
            [101000000, 202000000],
            datetime(2019, 9, 15, 14, 50, 3, 42042, timezone(timedelta(hours=9))),
            42042043,
            "Hello String"
        )]
    )

    res = clickhouse.data_string2type_value(src)
    assert expected == (res[0], res[2])


def test_return_values_with_specivied_types():
    src = """
    {
      "datetime"  : "2019/09/15 14:50:03.042042043 +0900"
    }
    """
    specified_types = {
        "datetime": "String"
    }

    expected = (
        tuple(["datetime"]),
        tuple(["String"]),
        [tuple(["2019/09/15 14:50:03.042042043 +0900"])]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res


def test_return_values_with_specivied_nested_types():
    src = """
    {
      "datetime"  : {
         "nested" : "2019/09/15 14:50:03.042042043 +0900"
      }
    }
    """
    specified_types = {
        "datetime__nested": "String"
    }

    expected = (
        tuple(["datetime__nested"]),
        tuple(["String"]),
        [tuple(["2019/09/15 14:50:03.042042043 +0900"])]
    )

    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res


def test_return_String_type_if_provide_None_type():
    src = """
    { "value" : null }
    """

    expected = (
        tuple(["value"]),
        tuple(["String"]),
        [tuple([None])]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_csv_if_complex_expressions():
    src = """
    a,'b hoge',large, "c,fuga","none?"
    10,"20","2,000",",,,",
    """

    expected = (
        ("a", "'b hoge'", "large", "c,fuga", "none?"),
        ("Float64", "Float64", "String", "String", "String"),
        [(10, 20, "2,000", ",,,", None)]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res
