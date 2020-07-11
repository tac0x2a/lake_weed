import json
import csv
import logging
import collections
import pandas as pd
import math

from io import StringIO
from . import util

Invalid: str = "invalid"
Json: str = "json"             # Json single obuject
JsonLines: str = "json_lines"  # Json lines (list of json object)
Csv: str = "csv"               # CSV with header


def inference_format(src: str, specified_types=None, json_delimiter="__", logger=logging.getLogger("lakeweed__format_inferencer")) -> (str, list, list):
    """
    Apply specified_types and try to parse string as date time.

    Returns:
        dict -- return converted flatten_dict. Keys will not be modified.}
    """

    if specified_types is None:
        specified_types = {}

    keys = []
    values_list = []

    # Json (single object)
    if __is_json(src, json_delimiter, specified_types, logger, keys, values_list):
        return Json, keys, values_list

    # Json Lines
    if __is_multi_jsons(src, json_delimiter, specified_types, logger, keys, values_list):
        return JsonLines, keys, values_list

    # CSV with header
    if __is_csv(src, logger, keys, values_list):
        return Csv, keys, values_list

    return Invalid, [], []


def __is_json(src, delimiter, specified_types, logger, keys: list, values_list: list) -> bool:
    try:
        body = json.loads(src)
        flatten_body = util.flatten(body, delimiter=delimiter)
        casted_body = util.traverse_casting(flatten_body, specified_types)

        keys.extend(casted_body.keys())
        values_list.append(list(casted_body.values()))

        return True

    except json.JSONDecodeError:
        logger.debug(f"{src}: is not JSON")
        return False


def __is_multi_jsons(raw_src, delimiter, specified_types, logger, keys: list, values_list: list) -> bool:
    src = raw_src.strip()
    lines = [s.strip() for s in src.split('\n')]

    # Line count is less than 1, it's not multiline json.
    if len(lines) <= 1:
        logger.debug(f"{src}: is not JSON multiline because row count is too few ({len(lines)})")
        return False

    unique_keys = collections.OrderedDict()  # to make unique key set
    key_value_list = []

    for line in lines:
        single_keys = []
        single_values = []
        if not __is_json(line, delimiter, specified_types, logger, single_keys, single_values):
            logger.debug(f"Found line is not JSON in L:{len(values_list)+1}")
            return False

        # If JSONs has different keys each other, this function will return union set of keys
        tmp_key_value = {}
        for idx, k in enumerate(single_keys):
            if k not in unique_keys.keys():
                # new key is found.
                unique_keys[k] = True
            tmp_key_value[k] = single_values[0][idx]  # value will be store single list into __is_json.

        key_value_list.append(tmp_key_value)

    # All lines are already read at here.
    for key_value in key_value_list:

        values_in_this_line = []
        for uk in unique_keys:
            v = key_value[uk] if uk in key_value.keys() else None
            values_in_this_line.append(v)

        values_list.append(values_in_this_line)

    keys.extend(unique_keys.keys())
    # All lines are able to parse as Json !
    return True


def __is_csv(raw_src, logger, keys: list, values_list: list) -> bool:
    src = raw_src.strip()

    # Line count is less than 1, it's csv only header or not csv.
    if len(src.split()) <= 1:
        logger.debug(f"{src}: is not CSV because row count is too few ({len(src.split())})")
        return False

    # If pandas can read src as csv, it is guessed csv.
    try:
        with StringIO(src) as io:
            df = pd.read_csv(io, skipinitialspace=True)

            keys.extend(list(df.columns))

            for row in df.values:
                values = [None if type(v) is float and math.isnan(v) else v for v in row.tolist()]
                values_list.append(values)
        return True
    except ValueError as e:
        logger.debug(f"{src}: is not CSV. {e}")
        return False
