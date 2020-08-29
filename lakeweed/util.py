
from . import time_parser


def flatten(src: dict, target=None, prefix="", delimiter="."):
    if target is None:
        target = {}

    for k, v in src.items():
        key_name = f"{prefix}{k}"

        if type(v) is dict:
            if len(v) <= 0:
                target[key_name] = {}
            else:
                flatten(v, target=target, prefix=f"{key_name}{delimiter}", delimiter=delimiter)
        else:
            target[key_name] = v

    return target


def data_types(values) -> list:
    return [__data_type(v) for v in values]


def __data_type(value):
    if value is None:
        return None

    if type(value) is list:
        return __data_type_list(value)
    if type(value) in (float, int):
        return 'Float'
    if type(value) is bool:
        return 'Bool'
    # value is string
    try:
        time_parser.elastic_time_parse(str(value)).tupple()
        return 'DateTime'
    except ValueError:
        pass
    except Exception:
        pass  # Todo logging

    return 'String'


def __data_type_list(value_as_list):
    if len(value_as_list) <= 0:
        return 'Array(Empty)'

    # Todo: decide tye by upcast_data_types.
    inner_value = value_as_list[0]
    inner_type = __data_type(inner_value)
    return f"Array({inner_type})"


# -----------------------------------------------------------------
__TypeMap = {
    # sorted(["empty", "float", "bool", "datetime", "array(string)", "string"])
    # ['array(string)', 'bool', 'datetime', 'empty', 'float', 'string']

    # "Bool" + "Bool": "Bool",
    # "Bool" + "DateTime": "String",
    "Bool" + "Float": "Float",
    # "Bool" + "String": "String",

    # "DateTime" + "DateTime": "DateTime",
    # "DateTime" + "Float": "String",
    # "DateTime" + "String": "String",

    # "Float" + "Float": "Float",
    # "Float" + "String": "String",
    # "String" + "String": "String"
}

def upcast_data_types(types_list) -> list:
    if len(types_list) <= 0:
        return []

    import copy
    upcasted_type = copy.deepcopy(types_list[0])

    for types in types_list:
        upcasted_type = [__upcast_data_type(t1, t2) for t1, t2 in zip(upcasted_type, types)]

    return upcasted_type


def __upcast_data_type(type1, type2) -> str:
    if type1 is None:
        return type2
    if type2 is None:
        return type1
    if type1 == type2:
        return type1

    # If type1 and type2 are array both, upcast inner type.
    type1_inner = get_array_inner_type(type1)
    type2_inner = get_array_inner_type(type2)
    if None not in [type1_inner, type2_inner]:
        if type1_inner == "Empty":
            return type2
        if type2_inner == "Empty":
            return type1

        from_to = "".join(sorted([type1_inner, type2_inner]))
        inner_type = __TypeMap.get(from_to, "String")
        return f"Array({inner_type})"

    from_to = "".join(sorted([type1, type2]))
    return __TypeMap.get(from_to, "String")


# -----------------------------------------------------------------
__AliasTypes = {
    'FLOAT': "Float",
    'DOUBLE': "Float",
    'INT': "Int",
    'INTEGER': "Int",
    'BOOL': "Bool",
    'BOOLEAN': "Bool",
    'DATETIME': "DateTime",
    'STR': "String",
    'STRING': "String"
}


def specified_type2lakeweed_type(specified_type):
    return __AliasTypes.get(specified_type.upper(), specified_type)


# -----------------------------------------------------------------
def get_array_inner_type(array_type: str) -> str:
    import re
    pattern = re.compile(r"Array\((.+)\)", re.IGNORECASE)
    inner_type_m = pattern.match(array_type)

    if inner_type_m is None:
        return None

    return inner_type_m.group(1)
