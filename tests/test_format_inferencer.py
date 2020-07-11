
from lakeweed import format_inferencer as fi


def test_inference_format_reteurn_Invalid_src_is_not_formated():
    src = """
    hello!
    """

    format = fi.inference_format(src)
    assert format == fi.Invalid


def test_inference_format_reteurn_json_src_is_sipmle_json():
    src = """
    {}
    """

    format = fi.inference_format(src)
    assert format == fi.Json

def test_inference_format_reteurn_list_of_json_src_is_multi_line_json_objects():
    src = """
    {}
    {}
    """

    format = fi.inference_format(src)
    assert format == fi.JsonLines


def test_inference_format_reteurn_csv_src_is_basic_csv():
    src = """
    sample_column01,b,c,d,e
    10,,"hello,world",,
    """

    format = fi.inference_format(src)
    assert format == fi.Csv
