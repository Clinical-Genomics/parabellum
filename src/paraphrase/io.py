from pathlib import Path
import coloredlogs
import yaml
import json
import logging
from .exceptions import JSONLoadError, YAMLLoadError
from typing import Dict

coloredlogs.install(level="INFO")
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def load_yaml(file: Path):
    try:
        with file.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise YAMLLoadError(f"Failed to read YAML file {file}: {e}")


def load_json(file: Path):
    """Load one JSON file and process its contents."""
    try:
        with file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise JSONLoadError(f"Failed to read JSON file {file}: {e}")


def print_tsv(json_data: Dict) -> None:
    """
    Print results in TSV format.
    """
    print("sample\tlocus\tstatus\tmetric\tvalue")

    for sample, locus in json_data.items():
        for locus, locus_info in locus.items():
            # Gene-level status comes from the rules engine; if no rules were
            # defined or no status was set, report it as "unknown"
            locus_status = locus_info.get("status")
            if not isinstance(locus_status, str):
                locus_status = "unknown"

            # Iterate over locus information, e.g. region_depth, final_haplotypes, etc.
            for locus_metric, locus_metric_value in locus_info.items():
                # Do not emit the per-gene status or rule-match metadata as separate rows
                if locus_metric in {"status", "status_matches"}:
                    continue
                prettified_value = stringify_value(locus_metric_value)
                print(
                    f"{sample}\t{locus}\t{locus_status}\t{locus_metric}\t{prettified_value}"
                )


def stringify_value(content) -> str | None:
    """
    Flatten nested dicts/lists for TSV output.

    Rules:
        - Skip empty or None values.
        - Dicts: key:value for top-level, key=subkey=subvalue for nested dicts
        - Lists:
            * Lists of simple values (str, int, float) are joined by commas.
            * Lists of lists -> join inner list by '|', then outer by ','
    """
    if content in (None, [], {}):
        return None

    if isinstance(content, (int, float, str)):
        return str(content)

    if isinstance(content, list):
        # If it's a list of simple values, join by commas
        if all(not isinstance(item, list) for item in content):
            flat = [str(element) for element in content if element is not None]
            return ",".join(flat) if flat else None
        else:
            # Lists with sublists
            flat = []
            for item in content:
                if isinstance(item, list):
                    if inner := [
                        str(element) for element in item if element is not None
                    ]:
                        flat.append("|".join(inner))
                    elif item is not None:
                        flat.append(str(item))
            return ",".join(flat) if flat else None

    if isinstance(content, dict):
        flat = []
        for key, value in content.items():
            if value in (None, [], {}):
                continue
            if isinstance(value, dict):
                sub_items = []
                for subkey, subvalue in value.items():
                    if prettified_subvalue := stringify_value(subvalue):
                        sub_items.append(f"{subkey}={prettified_subvalue}")
                if sub_items:
                    flat.append(f"{key}:{'|'.join(sub_items)}")
            else:
                if prettified_string := stringify_value(value):
                    flat.append(f"{key}:{prettified_string}")
        return ",".join(flat) if flat else None

    return str(content)
