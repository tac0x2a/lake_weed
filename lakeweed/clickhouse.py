import json
import logging

from .time_parser import DateTimeWithNS
from .inferencial_parser import inferencial_parse


def data_string2type_value(src_json_str: str, specified_types=None, logger=logging.getLogger("lakeweed__clickhouse")) -> (tuple, tuple, list):
    """
    Convert json string to python dict with data types for Clickhouse

    Arguments:
        src_str {str} -- Json, JsonLines, or CSV string.

    Keyword Arguments:
        logger -- logger object (default: {logging.getLogger("lakeweed__clickhouse")})

    Returns:
        tuple -- return tuple (columns, types, values_list).
            columns -- tuple of column name.
                       In Json, all nested kays(properties) are fltten.
                       In JsonLines, if JSONs has different keys each other, this function will return union set of keys.

            types -- A tuple of column type name for clickhouse.
                     Order of inside list values correspond to a columns order.

            values_list -- List of values tuple. Inside tuple correspoind to a record. For example, src string contains 2 records, length of Record List will be 2.
                           Order of inside list values correspond to a columns order. In JsonLines, if there is not key in some record, will be set None value.
    """

    (format, keys, values_list) = inferencial_parse(src_json_str, specified_types, "__", logger)

    columns_res = []
    types_res = []
    values_list_res = []

    # specified type
    for values in values_list:

        types_tmp = []
        values_tmp = []

        for key, value in zip(keys, values):
            __datastring2lcickhouse_sub(key, value, columns_res, types_tmp, values_tmp)
            types_res = types_tmp  # Todo need to integrate type

        values_list_res.append(tuple(values_tmp))

    return (tuple(columns_res), tuple(types_res), values_list_res)


def __datastring2clickhouse_sub_list(key, list, columns: list, types: list, values: list):
    columns.append(key)
    array_type = "Array(String)"
    items = []

    array_type_ns = None
    items_ns = []

    # Test for each element.
    # If value is dict, store dict as json.
    # If value is date time, store additional column has nano sec.
    for idx_i, v in enumerate(list):
        if isinstance(v, type(list)) or (type(v) is dict):
            items.append(json.dumps(v))
            continue

        idx = str(idx_i)
        temp_column = []
        temp_type = []
        temp_value = []

        __datastring2lcickhouse_sub(idx, v, temp_column, temp_type, temp_value)
        items.append(temp_value[0])
        array_type = "Array({})".format(temp_type[0])

        # for DateTime Array
        if len(temp_value) > 1:
            items_ns.append(temp_value[1])
            array_type_ns = "Array({})".format(temp_type[1])

    types.append(array_type)
    values.append(items)

    # for DateTime Array
    if len(items_ns) > 0:
        types.append(array_type_ns)
        columns.append(key + "_ns")
        values.append(items_ns)

    return


def __datastring2lcickhouse_sub(key, body, columns: list, types: list, values: list):
    if type(body) is list:
        __datastring2clickhouse_sub_list(key, body, columns, types, values)
        return

    # is atomic type.
    value = body
    columns.append(key)

    if type(value) is float:
        values.append(float(value))
        types.append("Float64")
        return
    if type(value) is int:
        values.append(int(value))
        types.append("Float64")
        return
    if type(value) is bool:
        values.append(1 if value else 0)
        types.append("UInt8")
        return
    if type(value) is DateTimeWithNS:
        (dt, ns) = value.tupple()
        values.append(dt)
        types.append("DateTime")
        # Clickhouse can NOT contain ms in DateTime column.
        columns.append(key + "_ns")
        values.append(ns)
        types.append("UInt32")
        return
    if value is None:
        values.append(None)
        # Todo: Need to find the table is already created.
        types.append("String")
        return

    values.append(str(value))
    types.append("String")

    return
