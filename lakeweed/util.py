
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


def traverse_casting(flatten_dict: dict, specified_types=None) -> dict:
    if specified_types == None:
        specified_types = {}

    new_items = {}
    for k, v in flatten_dict.items():

        # Convert specified type
        if k in specified_types.keys():
            specified_type = specified_types[k]

            try:
                new_items[k] = __cast_specified(v, specified_type)
            except TypeError:
                new_items[k] = v
                pass  # TODO logging or abort

        # Convert elastic type
        else:
            new_items[k] = __datetime_parse(v)

    return new_items


def __datetime_parse(value):
    # list
    if type(value) is list:
        return __traverse_datetime_parse_list(value)

    # scala
    if type(value) is str:
        try:
            return time_parser.elastic_time_parse(value)
        except ValueError:
            return value

    return value


def __traverse_datetime_parse_list(list: list):
    try:
        return [time_parser.elastic_time_parse(v) for v in list]
    except (ValueError, TypeError):
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
