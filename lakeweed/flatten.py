
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
