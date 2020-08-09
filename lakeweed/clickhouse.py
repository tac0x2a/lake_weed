import json
import logging
from collections import OrderedDict

from .time_parser import elastic_time_parse
from .inferencial_parser import inferencial_parse
from .util import data_types, upcast_data_types, specified_type2lakeweed_type, get_array_inner_type


def data_string2type_value(src_str: str, specified_types={}, logger=logging.getLogger("lakeweed__clickhouse")) -> (tuple, tuple, list):
    """
    Convert string to python dict with data types for Clickhouse

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

    (format, src_keys, src_values_list) = inferencial_parse(src_str, specified_types, "__", logger)

    # 1. Mapping type of value in src_values_list to lakeweed supporeted types.
    src_types_list = [data_types(values) for values in src_values_list]

    # 2. Upcasting types
    upcasted_types = upcast_data_types(src_types_list)

    # 3. Overwrite by specified_types if exists
    column_types = OrderedDict()
    for c, t in zip(src_keys, upcasted_types):
        column_types[c] = t

    for k, t in specified_types.items():
        if k not in column_types:
            continue
        column_types[k] = specified_type2lakeweed_type(t)

    # 4. [Depends on DBMS] If the type could not be estimated, it should be a String because there is no information to estimate it
    for c, t in column_types.items():
        if t is None:
            column_types[c] = 'String'
            continue
        inner_type = get_array_inner_type(t)
        if inner_type == 'Empty':
            column_types[c] = 'Array(String)'
        if inner_type == 'None':
            column_types[c] = 'Array(String)'


    # 5. [Depends on DBMS] Converting values according to the type and add columns if necessary
    ch_values_list = []
    ch_column_types = OrderedDict()
    for values in src_values_list:
        ch_values = []
        for c, t, v in zip(column_types.keys(), column_types.values(), values):
            ch_ctv_list = __data_value_specified(c, v, t)
            for ch_c, ch_t, ch_v in ch_ctv_list:
                ch_column_types[ch_c] = ch_t
                ch_values.append(ch_v)
        ch_values_list.append(tuple(ch_values))

    columns_res = tuple(ch_column_types.keys())
    types_res = tuple(ch_column_types.values())

    return (columns_res, types_res, ch_values_list)


def __data_value_specified(column, value, specified_type, depth=0) -> list:
    t = str(specified_type).upper()

    if t.startswith("ARRAY"):
        return __list_data_value_specified(column, value, specified_type, depth)

    if t in ["FLOAT"]:
        v = convert_or_default(lambda: float(value), None)
        return [(column, "Float64", v)]
    if t in ["INT"]:
        v = convert_or_default(lambda: int(value), None)
        return [(column, "Int64", v)]
    if t in ['BOOL']:
        v = convert_or_default(lambda: 1 if bool(value) else 0, None)
        if value is None:
            v = None
        return [(column, "UInt8", v)]
    if t == 'DATETIME':
        (dt, ns) = convert_or_default(lambda: elastic_time_parse(str(value)).tupple(), (None, None))
        return [(column, "DateTime", dt), (f"{column}_ns", "UInt32", ns)]
    if t in ['STRING', 'STR']:
        if isinstance(value, (list, dict, bool)):
            value = convert_or_default(lambda: json.dumps(value), None)
        v = convert_or_default(lambda: None if value is None else str(value), None)
        return [(column, "String", v)]
    # Todo need verify spec file method.
    logging.warning(f"Specified type '{str(specified_type)}' is not supported.")
    return [(column, None, value)]


def __list_data_value_specified(column, list_value, specified_type, depth) -> list:  # [(column, "Array(Type)", value), ]

    if depth > 0:
        json_str = convert_or_default(lambda: json.dumps(list_value), None)
        return [(column, f"String", json_str)]

    inner_type = get_array_inner_type(specified_type)

    values = []
    ctv_list = __data_value_specified("dummy", None, inner_type, depth + 1)
    dummy, values_type, dummy = ctv_list[0]

    if list_value is None or not isinstance(list_value, (list)):
        res = [(column, f"Array({values_type})", [])]
        if values_type == "DateTime":
            (col, typ, val) = ctv_list[1]
            res.append((f"{column}_ns", f"Array({typ})", []))
        return res

    values_ns = []
    values_ns_type = None

    for v in list_value:
        ctv_list = __data_value_specified("dummy", v, inner_type, depth + 1)
        (col, typ, val) = ctv_list[0]
        values.append(val)
        values_type = typ

        # If value is date time, store additional column has nano sec.
        if len(ctv_list) > 1:
            (col, typ, val) = ctv_list[1]
            values_ns.append(val)
            values_ns_type = typ

    res = [(column, f"Array({values_type})", values)]
    if values_type == "DateTime" or len(values_ns) > 1:
        res.append((f"{column}_ns", f"Array({values_ns_type})", values_ns))

    return res


def convert_or_default(value_lambda, default):
    try:
        return value_lambda()
    except TypeError:
        return default
    except ValueError:
        return default
