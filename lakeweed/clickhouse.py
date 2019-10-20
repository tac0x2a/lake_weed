import json
import datetime
from dateutil.tz import tzutc
import logging

from . import time_parser
from .time_parser import DateTimeWithNS
from . import util


def json2type_value(src_json_str: str, specified_types=None, logger=logging.getLogger("lakeweed__clickhouse")) -> tuple:
    """
    Convert json string to python dict with data types for Clickhouse

    Arguments:
        src_json_str {str} -- JSON string

    Keyword Arguments:
        logger -- logger object (default: {logging.getLogger("lakeweed__clickhouse")})

    Returns:
        tuple -- return tuple (types, values). types={"column":"type on clickhouse", ...}, values={"column":"value on clickhouse", ...}
    """

    if specified_types == None:
        specified_types = {}

    # flatten
    body = json.loads(src_json_str)
    flatten_body = util.flatten(body, delimiter="__")

    # convert types
    casted_body = util.traverse_casting(flatten_body, specified_types)

    # specified type
    types = {}
    values = {}

    for key, value in casted_body.items():
        __json2lcickhouse_sub(key, value, types, values)

    return (types, values)


def __json2clickhouse_sub_list(key, list, types, values):
    items = []
    items_ns = []
    types[key] = "Array(String)"
    for idx_i, v in enumerate(list):
        if isinstance(v, type(list)) or (type(v) is dict):
            items.append(json.dumps(v))
            continue

        idx = str(idx_i)
        temp_type = {}
        temp_value = {}

        __json2lcickhouse_sub(idx, v, temp_type, temp_value)
        items.append(temp_value[idx])

        types[key] = "Array({})".format(temp_type[idx])

        # for DateTime Array
        if (idx + "_ns") in temp_type.keys():
            items_ns.append(temp_value[idx + "_ns"])
            types[key + "_ns"] = "Array({})".format(temp_type[idx + "_ns"])

    values[key] = items

    # for DateTime Array
    if len(items_ns) > 0:
        values[key + "_ns"] = items_ns

    return


def __json2lcickhouse_sub(key, body, types, values):
    if type(body) is list:
        __json2clickhouse_sub_list(key, body, types, values)
        return

    # is atomic type.
    value = body

    if type(value) is float:
        values[key] = float(value)
        types[key] = "Float64"
        return
    if type(value) is int:
        values[key] = int(value)
        types[key] = "Float64"
        return
    if type(value) is bool:
        values[key] = 1 if value else 0
        types[key] = "UInt8"
        return
    if type(value) is DateTimeWithNS:
        (dt, ns) = value.tupple()
        values[key] = dt
        types[key] = "DateTime"
        # Clickhouse can NOT contain ms in DateTime column.
        values[key + "_ns"] = ns
        types[key + "_ns"] = "UInt32"
        return

    values[key] = str(value)
    types[key] = "String"

    return
