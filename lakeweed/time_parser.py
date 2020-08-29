import datetime
import re
from dataclasses import dataclass
from datetime import timezone

import pytz
from dateutil.parser import parse

NanosecPattern = re.compile(r".+\.(\d+).*")
RequiredTimePattern = re.compile(r".*\d\d?[/:-]\d\d?.*")


@dataclass
class DateTimeWithNS:
    datetime: datetime.datetime
    nanosec: int
    original_string: str

    def tupple(self) -> (datetime.datetime, int):
        return (self.datetime, self.nanosec)

    def __str__(self) -> str:
        return self.original_string

    @classmethod
    def parse(cls, datetime_like_string: str, tz_str=None):
        return elastic_time_parse(datetime_like_string, tz_str=tz_str)


def elastic_time_parse(src, tz_str=None, logger=None) -> DateTimeWithNS:
    """Parse src string as datetime and nanosec part. Raise exception if src format is NOT valid. """
    if src is None:
        raise ValueError

    if not re.match(RequiredTimePattern, src):
        raise ValueError

    nano = 0
    ret = parse(src)
    if ret.tzinfo is None:
        try:
            tz_info = pytz.timezone(tz_str)
            offset = timezone(tz_info.utcoffset(ret))
            ret = ret.replace(tzinfo=offset)
        except Exception:
            ret = ret.replace(tzinfo=timezone.utc)

    m = NanosecPattern.match(src)
    if(m is not None):
        nano = int(m.group(1)[0:9].ljust(9, '0'))

    return DateTimeWithNS(ret, nano, src)
