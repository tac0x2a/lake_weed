
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


def __cast_specified(original, specified: str):
    s = specified.upper()
    if s in ["STR", "STRING"]:
        return str(original)
    if s in ["INT", "INTEGER"]:
        return int(original)
    if s in ["FLOAT", "DOUBLE", "DECIMAL", "DEC"]:
        return float(original)
    raise TypeError(f"Not supported specified type: {specified}")
