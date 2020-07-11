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
    if specified_types is None:
        specified_types = {}

    keys = []
    values_list = []

    # Json (single object)
    if __is_json(src, json_delimiter, logger, keys, values_list):
        return Json, keys, values_list

    # Json Lines
    if __is_multi_jsons(src, json_delimiter, logger, keys, values_list):
        return JsonLines, keys, values_list

    # CSV with header
    if __is_csv(src, logger, keys, values_list):
        return Csv, keys, values_list

    return Invalid, [], []


def __is_json(src, delimiter, logger, keys: list, values_list: list) -> bool:
    try:
        body = json.loads(src)
        flatten_body = util.flatten(body, delimiter=delimiter)
        values = []
        for k, v in flatten_body.items():
            keys.append(k)
            values.append(v)

        values_list.append(values)

        return True

    except json.JSONDecodeError:
        logger.debug(f"{src}: is not JSON")
        return False


def __is_multi_jsons(src, delimiter, logger, keys: list, values_list: list) -> bool:
    stripped_src = src.strip()
    lines = stripped_src.split('\n')
    line_count = len(lines)
    if line_count <= 1:
        logger.debug(f"{src}: is not JSON multiline because row count is too few ({line_count})")
        return False

    orderd_keys = collections.OrderedDict()  # to make unique key set
    for line in lines:
        tmp_keys = []
        tmp_value = []
        if not __is_json(line, delimiter, logger, tmp_keys, tmp_value):
            logger.debug(f"in Line Number: {len(values_list)+1}")
            return False

        tmp_key_value = {}
        for idx, k in enumerate(tmp_keys):
            if k not in orderd_keys.keys():
                orderd_keys[k] = True
            tmp_key_value[k] = tmp_value[0][idx]  # value will be store single list into __is_json.

        values_in_this_line = []
        for k in orderd_keys:
            v = None
            if k in tmp_key_value.keys():
                v = tmp_key_value[k]
            values_in_this_line.append(v)

        values_list.append(values_in_this_line)

    keys.extend(orderd_keys.keys())
    # All lines are able to parse as Json !
    return True


def __is_csv(src, logger, keys: list, values_list: list) -> bool:
    stripped_src = src.strip()
    line_count = len(stripped_src.split())

    if line_count <= 1:
        logger.debug(f"{src}: is not CSV because row count is too few ({line_count})")
        return False

    try:
        if not csv.Sniffer().has_header(stripped_src):
            return False

        dialect = csv.Sniffer().sniff(stripped_src)
        dialect.skipinitialspace = True

        with StringIO(stripped_src) as io:
            df = pd.read_csv(io)
            keys.extend(list(df.columns))
            for line in df.values:
                l = [None if type(v) is float and math.isnan(v) else v for v in line.tolist()]
                values_list.append(l)

        return True

    except ValueError as e:
        logger.debug(f"{src}: is not CSV. {e}")
        pass
