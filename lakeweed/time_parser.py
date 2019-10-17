import time

from dateutil.parser import parse
from dateutil.tz import tzutc

import re

NanosecPattern = re.compile(r".+\.(\d+).*")
RequiredTimePattern = re.compile(r".*\d\d?[/:-]\d\d?.*")

def elastic_time_parse(src, logger = None):
    """Parse src string as datetime and nanosec part. Raise exception if src format is NOT valid. """
    nano = 0

    if not re.match(RequiredTimePattern, src):
        raise ValueError

    ret = parse(src)
    if ret.tzinfo == None:
        ret = ret.replace(tzinfo = tzutc())

    m = NanosecPattern.match(src)
    if(m != None):
        nano = int(m.group(1)[0:9].ljust(9, '0'))

    return [ret, nano]
