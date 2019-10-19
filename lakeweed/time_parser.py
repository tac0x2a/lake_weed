from dataclasses import dataclass
import time

import datetime
from dateutil.parser import parse
from dateutil.tz import tzutc

import re

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


def elastic_time_parse(src, logger=None) -> DateTimeWithNS:
    """Parse src string as datetime and nanosec part. Raise exception if src format is NOT valid. """
    nano = 0

    if not re.match(RequiredTimePattern, src):
        raise ValueError

    ret = parse(src)
    if ret.tzinfo == None:
        ret = ret.replace(tzinfo=tzutc())

    m = NanosecPattern.match(src)
    if(m != None):
        nano = int(m.group(1)[0:9].ljust(9, '0'))

    return DateTimeWithNS(ret, nano, src)
