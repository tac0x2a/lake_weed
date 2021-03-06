from datetime import datetime, timezone, timedelta

from lakeweed import clickhouse

from lakeweed.time_parser import DateTimeWithNS


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


def test_return_DateTime64_type_if_DateTime_like_string_provided():
    src = """
    { "hello" : "2018/11/14", "world" : "2018/11/15 11:22:33.123456789", "hoge" : "2018/13/15 11:22:33"}
    """
    expected = (
        ("hello", "world", "hoge"),
        ("DateTime64(6)", "DateTime64(6)", "String"),
        [
            (
                datetime(2018, 11, 14, 0, 0, 0, 0, timezone(timedelta(hours=0))),
                datetime(2018, 11, 15, 11, 22, 33, 123456, timezone(timedelta(hours=0))),
                "2018/13/15 11:22:33"
            )
        ]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_DateTime64_type_if_DateTime_like_string_provided_csv():
    src = """
    hello, world, hoge
    "2018/11/14", "2018/11/15 11:22:33.123456789", "2018/13/15 11:22:33"
    """
    expected = (
        ("hello", "world", "hoge"),
        ("DateTime64(6)", "DateTime64(6)", "String"),
        [
            (
                datetime(2018, 11, 14, 0, 0, 0, 0, timezone(timedelta(hours=0))),
                datetime(2018, 11, 15, 11, 22, 33, 123456, timezone(timedelta(hours=0))),
                "2018/13/15 11:22:33"
            )
        ]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_DateTime64_type_with_specified_timezone():
    src = """
    { "use_offset" : "2019/08/15 01:39+09:00", "use_specified_without_offset" : "2019/08/15 01:39", "invalid" : "2019/08/15 01:60"}
    """
    expected = (
        ("use_offset", "use_specified_without_offset", "invalid"),
        ("DateTime64(6)", "DateTime64(6)", "String"),
        [
            (
                datetime(2019, 8, 15, 1, 39, 0, 0 * 1000, timezone(timedelta(hours=9))),
                datetime(2019, 8, 15, 1, 39, 0, 0 * 1000, timezone(timedelta(hours=-6))),
                "2019/08/15 01:60"
            )
        ]
    )
    res = clickhouse.data_string2type_value(src, tz_str="Canada/Mountain")
    assert expected == res


def test_return_DateTime64_list_with_specified_timezone():
    src = """
    { "use_offset" : ["2019/08/15 01:39+09:00"], "use_specified_without_offset" : ["2019/08/15 01:39"], "invalid" : ["2019/08/15 01:60"]}
    """
    expected = (
        ("use_offset", "use_specified_without_offset", "invalid"),
        ("Array(DateTime64(6))", "Array(DateTime64(6))", "Array(String)"),
        [
            (
                [datetime(2019, 8, 15, 1, 39, 0, 0 * 1000, timezone(timedelta(hours=9)))],
                [datetime(2019, 8, 15, 1, 39, 0, 0 * 1000, timezone(timedelta(hours=-6)))],
                ["2019/08/15 01:60"]
            )
        ]
    )
    res = clickhouse.data_string2type_value(src, tz_str="Canada/Mountain")
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


def test_return_DateTime64_array_if_DateTime_like_strings():
    src = """
    {"hello" : ["2018/11/14", "2018/11/15 11:22:33.123456789"]}
    """

    expected = (
        ("hello", ),
        ("Array(DateTime64(6))", ),
        [(
            [
                datetime(2018, 11, 14, 0, 0, 0, 0, timezone(timedelta(hours=0))),
                datetime(2018, 11, 15, 11, 22, 33, 123456, timezone(timedelta(hours=0))),
            ],
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


def test_return_NULL_Array_if_nulle_array():
    src = """
    { "null_array" : [null, 42, null]}
    """

    expected = (
        ("null_array", ),
        ("Array(String)", ),
        [([None, '42', None], )]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_NULL_Array_if_behind_nulle_array():
    src = """
    { "null_array" : [42, null, null]}
    """

    expected = (
        ("null_array", ),
        ("Array(Float64)", ),
        [([42, None, None], )]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res

def test_return_string_Array_if_nested_array():
    src = """
    { "nested" : [[[],[1,2,3]]]}
    """

    expected = (
        ("nested", ),
        ("Array(String)", ),
        [(['[[], [1, 2, 3]]'], )]
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
        ("array", "hello", "world__value", "hoge", "dates", "date", "str"),
        ("Array(Float64)", "Array(String)", "Array(String)", "Array(String)", "Array(DateTime64(6))", "DateTime64(6)", "String"),
        [(
            [1, 2, 3],
            ['[1.1, 2.2]', '[3.3, 4.4]'],
            ['[1, 2]', '[3, 4]'],
            ['{"v": 1}', '{"v": 2}'],
            [
                datetime(2019, 9, 15, 14, 50, 3, 101000, timezone(timedelta(hours=9))),
                datetime(2019, 9, 15, 14, 50, 3, 202000, timezone(timedelta(hours=9))),
            ],
            datetime(2019, 9, 15, 14, 50, 3, 42042, timezone(timedelta(hours=9))),
            "Hello String"
        )]
    )

    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_None_if_invalid_datetime_format_string_in_array():
    src = """
    {
      "datetime"  : ["2019/09/15 14:50:03", "hoge", "2019/09/15 14:50:04"]
    }
    """
    expected = (
        ("datetime", ),
        ("Array(DateTime64(6))", ),
        [(
            [
                datetime(2019, 9, 15, 14, 50, 3, 0, timezone(timedelta(hours=0))),
                None,
                datetime(2019, 9, 15, 14, 50, 4, 0, timezone(timedelta(hours=0))),
            ],
        )]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_values_with_specified_types():
    src = """
    {
      "datetime"  : "2019/09/15 14:50:03.042042043 +0900"
    }
    """
    specified_types = {
        "datetime": "String"
    }

    expected = (
        ("datetime", ),
        ("String", ),
        [("2019/09/15 14:50:03.042042043 +0900",)]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res


def test_return_values_with_specified_types_null():
    src = """
    {
      "i"  : "42",
      "d"  : "42",
      "n"  : null
    }
    """
    specified_types = {
        "i": "integer",
        "d": "double",
        "n": "double"
    }

    expected = (
        ("i", "d", "n"),
        ("Int64", "Float64", "Float64"),
        [(42, 42, None)]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res


def test_return_values_with_specified_types_if_property_not_found():
    src = """
    {"i"  : 42}
    {"j"  : 42}
    """
    specified_types = {
        "missing_column": "DateTime"
    }
    expected = (
        ("i", "j", "missing_column"),
        ("Float64", "Float64", "DateTime64(6)"),
        [(42, None, None), (None, 42, None)]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res


def test_return_values_empty_collection():
    src = """
    {"v": {}, "a": [], "av": [{}], "va": {"a": []} }
    """
    specified_types = {}
    expected = (
        ("v", "a", "av", "va__a"),
        ("String", "Array(String)", "Array(String)", "Array(String)"),
        [
            ("{}", [], ['{}'], [])
        ]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res


def test_return_values_without_specified_paramsl():
    src = """
    {"v": "42"}
    {"v":  42}
    {"v": true}
    {"v": null}
    {"v": "hoge42hoge"}
    {"v": "2020-08-09 11:46:00"}
    {"v": {}}
    {"v": []}
    {"v": [{}]}
    {"v": [42]}
    """
    specified_types = {}
    expected = (
        ("v", ),
        ("String", ),
        [
            ("42", ), ("42", ), ("true", ), (None, ), ("hoge42hoge", ),
            ("2020-08-09 11:46:00", ), ("{}", ), ("[]", ), ("[{}]", ), ("[42]", )
        ]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res


def test_return_values_with_float_valuel():
    src = """
    {"v": "42"}
    {"v":  42}
    {"v": true}
    {"v": null}
    {"v": "hoge42hoge"}
    {"v": "2020-08-09 11:46:00"}
    {"v": {}}
    {"v": [{}]}
    {"v": [42]}
    """
    specified_types = {"v": "float"}
    expected = (
        ("v", ),
        ("Float64", ),
        [(42.0,), (42.0,), (1.0,), (None,), (None,), (None,), (None,), (None,), (None,)]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res

def test_return_values_with_int_valuel():
    src = """
    {"v": "42"}
    {"v":  42}
    {"v": true}
    {"v": null}
    {"v": "hoge42hoge"}
    {"v": "2020-08-09 11:46:00"}
    {"v": {}}
    {"v": [{}]}
    {"v": [42]}
    """
    specified_types = {
        "v": "int"
    }
    expected = (
        ("v", ),
        ("Int64", ),
        [(42,), (42,), (1,), (None,), (None,), (None,), (None,), (None,), (None,)]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res

def test_return_values_with_bool_valuel():
    src = """
    {"v": "42"}
    {"v":  42}
    {"v": true}
    {"v": null}
    {"v": "hoge42hoge"}
    {"v": "2020-08-09 11:46:00"}
    {"v": {}}
    {"v": []}
    {"v": [{}]}
    {"v": [42]}
    """
    specified_types = {
        "v": "bool"
    }
    expected = (
        ("v", ),
        ("UInt8", ),
        [(1,), (1,), (1,), (None,), (1,), (1,), (0,), (0,), (1,), (1,)]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res


def test_return_values_with_date_time_valuel():
    src = """
    {"v": "42"}
    {"v":  42}
    {"v": true}
    {"v": null}
    {"v": "hoge42hoge"}
    {"v": "2020-08-09 11:46:00"}
    {"v": {}}
    {"v": []}
    {"v": [{}]}
    {"v": [42]}
    """
    specified_types = {
        "v": "datetime",
        "v_ns": "string"
    }
    expected = (
        ("v", "v_ns"),
        ("DateTime64(6)", "String"),
        [(None, None), (None, None), (None, None), (None, None), (None, None),
         (datetime(2020, 8, 9, 11, 46, 0, 0, timezone(timedelta(hours=0))), None),
         (None, None), (None, None), (None, None), (None, None)]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res


def test_return_values_with_string_valuel():
    src = """
    {"v": "42"}
    {"v":  42}
    {"v": true}
    {"v": null}
    {"v": "hoge42hoge"}
    {"v": "2020-08-09 11:46:00"}
    {"v": {}}
    {"v": []}
    {"v": [{}]}
    {"v": [42]}
    """
    specified_types = {
        "v": "string",
    }
    expected = (
        ("v", ),
        ("String", ),
        [
            ("42", ), ("42", ), ("true", ), (None, ), ("hoge42hoge", ),
            ("2020-08-09 11:46:00", ), ("{}", ), ("[]", ), ("[{}]", ), ("[42]", )
        ]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res


def test_return_array_values_with_string_valuel():
    src = """
    {"v": "42"}
    {"v": 42}
    {"v": true}
    {"v": null}
    {"v": "hoge42hoge"}
    {"v": "2020-08-09 11:46:00"}
    {"v": {}}
    {"v": []}
    {"v": [{}]}
    {"v": ["42"]}
    {"v": [42]}
    {"v": [true]}
    {"v": [null]}
    {"v": ["hoge42hoge"]}
    {"v": ["2020-08-09 11:46:00"]}
    """
    specified_types = {
        "v": "string",
    }
    expected = (
        ("v", ),
        ("String", ),
        [
            ("42", ), ("42", ), ("true", ), (None, ), ("hoge42hoge", ),
            ("2020-08-09 11:46:00", ), ("{}", ), ("[]", ), ("[{}]", ),
            ('["42"]', ), ('[42]', ), ('[true]', ), ('[null]', ), ('["hoge42hoge"]',), ('["2020-08-09 11:46:00"]', )
        ]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res


def test_return_array_values_with_array_string_valuel():
    src = """
    {"v": "42"}
    {"v": 42}
    {"v": true}
    {"v": null}
    {"v": "hoge42hoge"}
    {"v": "2020-08-09 11:46:00"}
    {"v": {}}
    {"v": []}
    {"v": [{}]}
    {"v": ["42"]}
    {"v": [42]}
    {"v": [true]}
    {"v": [null]}
    {"v": ["hoge42hoge"]}
    {"v": ["2020-08-09 11:46:00"]}
    """
    specified_types = {
        "v": "array(string)",
    }
    expected = (
        ("v", ),
        ("Array(String)", ),
        [
            ([], ), ([], ), ([], ), ([], ), ([], ),
            ([], ), ([], ), ([], ), (["{}"], ),
            (["42"], ), (["42"], ), (["true"], ), ([None], ), (["hoge42hoge"],), (["2020-08-09 11:46:00"], )
        ]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res

def test_return_array_values_with_array_datetime_valuel():
    src = """
    {"v": "42"}
    {"v": 42}
    {"v": true}
    {"v": null}
    {"v": "hoge42hoge"}
    {"v": "2020-08-09 11:46:00"}
    {"v": {}}
    {"v": []}
    {"v": [{}]}
    {"v": ["42"]}
    {"v": [42]}
    {"v": [true]}
    {"v": [null]}
    {"v": ["hoge42hoge"]}
    {"v": ["2020-08-09 11:46:00"]}
    """
    specified_types = {
        "v": "array(datetime)",
    }
    expected = (
        ("v", ),
        ("Array(DateTime64(6))", ),
        [
            ([], ), ([], ), ([], ), ([], ),
            ([], ), ([], ), ([], ), ([], ),
            ([None], ), ([None], ), ([None], ),
            ([None], ), ([None], ), ([None], ),
            ([datetime(2020, 8, 9, 11, 46, 0, 0, timezone(timedelta(hours=0)))], )
        ]
    )
    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res


def test_return_values_with_specified_nested_types():
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
        ("datetime__nested", ),
        ("String", ),
        [("2019/09/15 14:50:03.042042043 +0900", )]
    )

    res = clickhouse.data_string2type_value(src, specified_types=specified_types)
    assert expected == res


def test_return_String_type_if_provide_None_type():
    src = """
    { "value" : null }
    """

    expected = (
        ("value", ),
        ("String", ),
        [(None, )]
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


# --------------------------------
# Multi line Cases

def test_return_multi_empty_set():
    src = """
    {}
    {}
    {}
    """
    expected = ((), (), [(), (), ()])
    res = clickhouse.data_string2type_value(src)
    assert res == expected


def test_return_multi_basic_type_and_values():
    src = """
    { "hello" : 42, "world" : 128.4, "bool" : true,  "str" : "Hello,World1" }
    { "hello" : 43, "world" : 128.5, "bool" : false, "str" : "Hello,World2" }
    { "hello" : 44, "world" : 128.6, "bool" : true,  "str" : "Hello,World3" }
    """

    expected = (
        ("hello", "world", "bool", "str"),
        ("Float64", "Float64", "UInt8", "String"),
        [
            (42, 128.4, 1, "Hello,World1"),
            (43, 128.5, 0, "Hello,World2"),
            (44, 128.6, 1, "Hello,World3")
        ]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_types_with_inoreing_null_value():
    src = """
    { "f" : 42,   "b" : true, "d": "2019/09/15 14:50:03.101 +0900", "s" : "Hello,World" }
    { "f" : null, "b" : null, "d": null,                            "s" : null }
    """

    expected = (
        ("f", "b", "d", "s"),
        ("Float64", "UInt8", "DateTime64(6)", "String"),
        [
            (42, 1, datetime(2019, 9, 15, 14, 50, 3, 101000, timezone(timedelta(hours=9))), "Hello,World"),
            (None, None, None, None)
        ]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_types_with_optimal_value():
    src = """
    { "f" : 42,   "b" : true,   "d": "2019/09/15 14:50:03.101 +0900"}
    { "f" : "42", "b" : "true", "d": "2019/13/15 14:50:03.101 +0900"}
    """

    expected = (
        ("f", "b", "d"),
        ("String", "String", "String"),
        [
            ("42", "true", "2019/09/15 14:50:03.101 +0900"),
            ("42", "true", "2019/13/15 14:50:03.101 +0900"),
        ]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_types_csv_with_optimal_value():
    src = """
    f,b,d
    42,true,2019/09/15 14:50:03.101 +0900
    "42","true",2019/13/15 14:50:03.101 +0900
    """

    expected = (
        ("f", "b", "d"),
        ("Float64", "UInt8", "String"),
        [
            (42, 1, "2019/09/15 14:50:03.101 +0900"),
            (42, 1, "2019/13/15 14:50:03.101 +0900"),
        ]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_types_csv_with_none_value():
    src = """
    a,b,c
    42,,
    ,"true",2019/9/15 14:50:03.101 +0900
    """

    expected = (
        ("a", "b", "c"),
        ("Float64", "UInt8", "DateTime64(6)"),
        [
            (42, None, None),
            (None, 1, datetime(2019, 9, 15, 14, 50, 3, 101000, timezone(timedelta(hours=9))))
        ]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res



def test_return_types_csv_all_none_value():
    src = """
    a,b,c
    ,,
    ,,
    """

    expected = (
        ("a", "b", "c"),
        ("String", "String", "String"),
        [
            (None, None, None),
            (None, None, None)
        ]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res


def test_return_empty_array_if_type_is_Array_value_is_null():
    src = """
    { "a" : [1,2,3] }
    { "a" : [] }
    { "a" : null }
    """

    expected = (
        ("a", ),
        ("Array(Float64)", ),
        [
            ([1, 2, 3], ),
            ([], ),
            ([], ) # Clickhouse Array is not nullable.
        ]
    )
    res = clickhouse.data_string2type_value(src)
    assert expected == res
