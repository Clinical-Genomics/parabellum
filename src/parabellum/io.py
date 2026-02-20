from pathlib import Path
import coloredlogs
import yaml
import json
import logging
import sys
from .exceptions import JSONLoadError, YAMLLoadError
from typing import Dict, List, Tuple

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
                print(f"{sample}\t{locus}\t{locus_status}\t{locus_metric}\t{prettified_value}")


def stringify_value(content) -> str | None:
    """
    Flatten nested dicts/lists for TSV output.
    - Skip empty or None values.
    - Top-level dict: key:value
    - Nested dicts: key=subkey=subvalue
    - Lists: joined by commas

    value can be a string, int, float, list, or dict.
    """
    if content in (None, [], {}):
        return None

    if isinstance(content, (int, float, str)):
        return str(content)

    if isinstance(content, list):
        flat = []
        for item in content:
            if isinstance(item, list):
                if inner := [str(element) for element in item if element is not None]:
                    flat.append(",".join(inner))
            elif item is not None:
                flat.append(str(item))
        return "|".join(flat) if flat else None

    if isinstance(content, dict):
        flattened_items = []
        for key, value in content.items():
            if value in (None, [], {}):
                continue
            if isinstance(value, dict):
                sub_items = []
                for subkey, subvalue in value.items():
                    prettified_subvalue = stringify_value(subvalue)
                    if prettified_subvalue is not None:
                        sub_items.append(f"{subkey}={prettified_subvalue}")
                if sub_items:
                    flattened_items.append(f"{key}:{'|'.join(sub_items)}")
            else:
                content_string = stringify_value(value)
                if content_string is not None:
                    flattened_items.append(f"{key}:{content_string}")
        return ";".join(flattened_items) if flattened_items else None

    return str(content)
