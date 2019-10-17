
import pytest
from br2dl import time_parser
from datetime import datetime, timezone, timedelta


def assertConverted(src, expected_time, expected_ns):
    res = time_parser.elastic_time_parse(src)
    assert [expected_time, expected_ns] == res


def assertNotValid(src):
    with pytest.raises(ValueError):
        time_parser.elastic_time_parse(src)

#   # ISO 8601: ex: "yyyy-mm-ddThh:MM:ss+OO:OO'"
#               '2018-12-03T12:34:56.123+08:00',
#               '2018-12-03T12:02:56Z',
#               '2018-12-03T12:34.334:56Z'


def test_return_time_value_if_string_is_ISO_8601_format():
    assertConverted("2018-12-03T12:34:56-12:00",
                    datetime(2018, 12, 3, 12, 34, 56, 0, timezone(timedelta(hours=-12))), 0
                    )


def test_return_original_string_Time_value_if_NOT_string_is_NOT_datetime_format():
    assertNotValid("2018-12-03T12:34:56-12:00 hoge")


def test_return_Time_value_if_string_is_ISO_8601_format_with_ns():
    assertConverted("2018-12-03T12:34:56.123456789+08:00",
                    datetime(2018, 12, 3, 12, 34, 56, 123456, timezone(timedelta(hours=8))), 123456789
                    )


def test_return_Time_value_if_string_is_ISO_8601_format_with_invalid_ns():
    assertNotValid("2018-12-03T12:34:56.hoge+08:00")


def test_return_Time_value_if_string_is_ISO_8601_format_missing_ns():
    assertConverted("2018-12-03T12:34:56.+08:00",
                    datetime(2018, 12, 3, 12, 34, 56, 0, timezone(timedelta(hours=8))), 0
                    )


def test_return_Time_value_if_string_is_ISO_8601_format_zero_ns():
    assertConverted("2018-12-03T12:34:56.0+08:00",
                    datetime(2018, 12, 3, 12, 34, 56, 0, timezone(timedelta(hours=8))), 0
                    )


def test_return_original_string_if_string_is_ISO_8601_like_format():
    assertNotValid("2018-12-03_12:34:56.123")

# RFC 2822: ex: 'Sun, 31 Aug 2008 12:08:19 +0900'


def test_return_Time_value_if_string_is_RFC_2616_format():
    assertConverted("Sun, 31 Aug 2008 12:34:56 GMT",
                    datetime(2008, 8, 31, 12, 34, 56, 0, timezone(timedelta(hours=0))), 0
                    )


def test_return_original_string_if_string_is_RFC_2616_format_with_ns():
    assertConverted("Sun, 31 Aug 2008 12:34:56.789123456 GMT",
                    datetime(2008, 8, 31, 12, 34, 56, 789123, timezone(timedelta(hours=0))), 789123456
                    )

# --------------------------------------------------------------------------


def test_return_Time_value_if_string_is_Date_like_format_splited_by_slash():
    # If timezone is not provided, make datetime with UTC.
    assertConverted("2018/11/14",
                    datetime(2018, 11, 14, 0, 0, 0, 0, timezone(timedelta(hours=0))), 0
                    )


def test_return_Time_value_if_string_is_Date_like_format_splited_by_hyphen():
    # If timezone is not provided, make datetime with UTC.
    assertConverted("2018-11-14",
                    datetime(2018, 11, 14, 0, 0, 0, 0 * 1000, timezone(timedelta(hours=0))), 0
                    )


def test_return_Time_value_if_string_is_Time_like_format_with_hour_min_by_slash():
    assertConverted("2018/11/14 09:06",
                    datetime(2018, 11, 14, 9, 6, 0, 0 * 1000, timezone(timedelta(hours=0))), 0
                    )


def test_return_Time_value_if_string_is_Time_like_format_with_hour_min_by_hyphen():
    assertConverted("2018-11-14 09:06",
                    datetime(2018, 11, 14, 9, 6, 0, 0 * 1000, timezone(timedelta(hours=0))), 0
                    )


def test_return_Time_value_if_string_is_Time_like_format_without_zero_padding():
    assertConverted("2018/11/14 9:6",
                    datetime(2018, 11, 14, 9, 6, 0, 0 * 1000, timezone(timedelta(hours=0))), 0
                    )


def test_return_original_string_is_simple_day_of_week():
    assertNotValid("Sat")


if __name__ == '__main__':
    pytest.main(['-v', __file__])
