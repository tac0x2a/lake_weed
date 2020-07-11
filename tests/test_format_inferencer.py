
from lakeweed import format_inferencer as fi


# -------------- Invalid -------------- #
def test_inference_format_reteurn_Invalid_src_is_not_formated():
    src = """
    hello!
    """

    (format, keys, values_list) = fi.inference_format(src)
    assert fi.Invalid == format
    assert keys == []
    assert values_list == []


# -------------- Json -------------- #
def test_inference_format_reteurn_json_src_is_sipmle_json():
    src = """
    {}
    """

    (format, keys, values_list) = fi.inference_format(src)
    assert fi.Json == format
    assert [] == keys
    assert [[]] == values_list


def test_inference_format_reteurn_json_obj_src_is_sipmle_json():
    src = """
    { "hello" : 42, "world" : 128.4, "bool" : true, "str" : "Hello,World" }
    """

    (format, keys, values_list) = fi.inference_format(src)
    assert fi.Json == format
    assert ['hello', 'world', 'bool', 'str'] == keys
    assert [[42, 128.4, True, 'Hello,World']] == values_list


# -------------- JsonLines -------------- #
def test_inference_format_reteurn_list_of_json_src_is_multi_line_json_objects():
    src = """
    {}
    {}
    """

    (format, keys, values_list) = fi.inference_format(src)
    assert fi.JsonLines == format
    assert [] == keys
    assert [[], []] == values_list


def test_inference_format_reteurn_list_of_json_obj_src_is_multi_line_json_objects():
    src = """
    { "a" : 42, "b" : 128.4, "d" : true, "e" : "Hello,World" }
    { "a" : 42, "b" : 128.4, "c" : true, "e" : "Hello,World" }
    """

    expected_keys = ['a', 'b', 'd', 'e', 'c']
    expected_values = [
        [42, 128.4, True, 'Hello,World', None],
        [42, 128.4, None, 'Hello,World', True]
    ]

    (format, keys, values_list) = fi.inference_format(src)
    assert fi.JsonLines == format
    assert expected_keys == keys
    assert expected_values == values_list


# -------------- CSV -------------- #
def test_inference_format_reteurn_csv_src_is_basic_csv():
    src = """
    a,b,c,d,e
    10,,"hello,world",,
    42,hoge,"hello,world",,
    """

    (format, keys, values_list) = fi.inference_format(src)
    assert fi.Csv == format
    assert ["a", "b", "c", "d", "e"] == keys
    assert [[10, None, "hello,world", None, None], [42, 'hoge', 'hello,world', None, None]] == values_list
