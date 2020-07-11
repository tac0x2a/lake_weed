import json
import csv
import logging


Invalid: str = "invalid"
Json: str = "json"             # Json single obuject
JsonLines: str = "json_lines"  # Json lines (list of json object)
Csv: str = "csv"               # CSV with header



def inference_format(src: str, logger=logging.getLogger("lakeweed__format_inferencer")) -> str:

    # Json (single object)
    if __is_json(src, logger):
        return Json

    # Json Lines
    if __is_multi_jsons(src, logger):
        return JsonLines

    # CSV with header
    if __is_csv(src, logger):
        return Csv

    return Invalid


def __is_json(src, logger) -> bool:
    try:
        json.loads(src)
        return True
    except json.JSONDecodeError:
        logger.debug(f"{src}: is not JSON")
        return False


def __is_multi_jsons(src, logger) -> bool:
    stripped_src = src.strip()
    lines = stripped_src.split()
    line_count = len(lines)
    if line_count <= 1:
        logger.debug(f"{src}: is not JSON multiline because row count is too few ({line_count})")
        return False

    line_number = 1
    for line in lines:
        if not __is_json(line, logger):
            logger.debug(f"in Line Number: {line_number}")
            return False

        line_number += 1

    # All lines are able to parse as Json !
    return True

def __is_csv(src, logger) -> bool:
    stripped_src = src.strip()
    line_count = len(stripped_src.split())

    if line_count <= 1:
        logger.debug(f"{src}: is not CSV because row count is too few ({line_count})")
        return False

    try:
        return csv.Sniffer().has_header(stripped_src)
    except ValueError as e:
        print(e)
        logger.debug(f"{src}: is not CSV")
        pass
