
from . import time_parser


def flatten(src: dict, target=None, prefix="", delimiter="."):

    if target == None:
        target = {}

    for k, v in src.items():
        key_name = f"{prefix}{k}"

        if type(v) is dict:
            flatten(v, target=target, prefix=f"{key_name}{delimiter}", delimiter=delimiter)
        else:
            target[key_name] = v

    return target


def traverse_datetime_parse(flatten_dict: dict):
    new_items = {}
    for k, v in flatten_dict.items():
        if type(v) is list:
            v = __traverse_datetime_parse_list(v)
        else:
            try:
                v = time_parser.elastic_time_parse(v)
            except ValueError:
                pass
        new_items[k] = v

    return new_items


def __traverse_datetime_parse_list(list: list):
    try:
        return [time_parser.elastic_time_parse(v) for v in list]
    except ValueError:
        return list


def __cast_specified(original, specified: str):
    s = specified.upper()
    if s in ["STR", "STRING"]:
        return str(original)
    if s in ["INT", "INTEGER"]:
        return int(original)
    if s in ["FLOAT", "DOUBLE", "DECIMAL", "DEC"]:
        return float(original)
    raise TypeError(f"Not supported specified type: {specified}")
