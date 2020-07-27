import json
import logging
from collections import OrderedDict

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

    name2type_value_map = []
    values_list_res = []
    types_integrated = OrderedDict()

    # specified type
    for values in values_list:
        (columns, types, values) = __data_string2type_value(keys, values, specified_types, logger)
        name2type_value_map.append({k: (t, v) for k, t, v in zip(columns, types, values)})

        # Detect data type for integration. Apply types after traverse all data.
        for new_col, new_type in zip(columns, types):
            if new_col not in types_integrated.keys():
                types_integrated[new_col] = new_type
                continue

            if new_type is None:  # always use current data type
                continue

            current_type = types_integrated[new_col]
            if current_type is None:  # always use new_type
                types_integrated[new_col] = new_type
                continue

            if current_type == new_type:
                continue


            (correct_type, converter) = __type_map(current_type, new_type)
            types_integrated[new_col] = correct_type

    # If all data is None, type regard as String
    for c, t in types_integrated.items():
        if t is None:
            types_integrated[c] = "String"

    # Remove nanosec column if DateTime column changed to String column.
    # If the column is not DateTime type, Nano-sec column is not required.
    date_columns = [c[0:-3] for c in types_integrated.keys() if c.endswith("_ns")]
    for dt_col in date_columns:
        if types_integrated[dt_col] not in ["DateTime", "Array(DateTime)"]:
            del types_integrated[dt_col + "_ns"]

    # Re-parse this values.
    for old_col_type_value_map in name2type_value_map:
        new_values = []
        for new_col, new_type in types_integrated.items():
            if new_col not in old_col_type_value_map.keys():
                new_values.append(None)
                continue

            (old_type, old_value) = old_col_type_value_map[new_col]
            if old_type is None:
                none_value = None
                if new_type.startswith("Array"):
                    none_value = []
                new_values.append(none_value)
                continue
            if old_type == new_type:
                new_values.append(old_value)
                continue

            (new_type, converter) = __type_map(old_type, new_type)
            new_value = converter(old_value)
            new_values.append(new_value)

        values_list_res.append(tuple(new_values))

    # values_list_res.append(tuple(values))

    columns_res = tuple(types_integrated.keys())
    types_res = tuple(types_integrated.values())

    return (columns_res, tuple(types_res), values_list_res)


def __data_string2type_value(keys: tuple, values: list, specified_types, logger) -> (tuple, tuple, list):

    columns_tmp = OrderedDict()
    types_tmp = []
    values_tmp = []

    for key, value in zip(keys, values):
        __datastring2lcickhouse_sub(key, value, columns_tmp, types_tmp, values_tmp)

    return (tuple(columns_tmp.keys()), tuple(types_tmp), values_tmp)



def __datastring2clickhouse_sub_list(key, list, columns: OrderedDict, types: list, values: list):
    columns[key] = True
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
        dummy_column = OrderedDict()
        temp_type = []
        temp_value = []

        __datastring2lcickhouse_sub(idx, v, dummy_column, temp_type, temp_value)
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
        columns[key + "_ns"] = True
        values.append(items_ns)

    return


def __datastring2lcickhouse_sub(key, body, columns: OrderedDict, types: list, values: list):
    if type(body) is list:
        __datastring2clickhouse_sub_list(key, body, columns, types, values)
        return

    # is atomic type.
    value = body
    columns[key] = True

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
        columns[key + "_ns"] = True
        values.append(ns)
        types.append("UInt32")
        return
    if value is None:
        values.append(None)
        # Todo: Need to find the table is already created.
        types.append(None)
        return

    values.append(str(value))
    types.append("String")

    return


__TypeMap = {
    # sorted(["Float64", "UInt8", "UInt32", "DateTime", "String"])
    # ['DateTime', 'Float64', 'String', 'UInt32', 'UInt8']

    # (From, To): lambda value: (converted_type, converted_value)
    "DateTime" + "Float64": ("String",  lambda v: str(v)),
    "DateTime" + "UInt8":   ("String", lambda v: str(v)),
    "DateTime" + "UInt32":  ("String", lambda v: str(v)),
    "DateTime" + "String":  ("String", lambda v: str(v)),

    "Float64" + "UInt8":    ("Float64", lambda v: float(v)),
    "Float64" + "UInt32":   ("Float64", lambda v: float(v)),
    "Float64" + "String":   ("String",  lambda v: str(v)),

    "String" + "UInt8" :    ("String", lambda v: str(v)),
    "String" + "UInt32":      ("String", lambda v: str(v)),

    "UInt32" + "UInt8":    ("UInt32", lambda v: v),
}


def __type_map(from_: str, to: str):
    from_to = "".join(sorted([str(s) for s in [from_, to]]))
    if from_to not in __TypeMap:  # Todo collection support.
        return ("String", lambda v: str(v))
    return __TypeMap[from_to]
