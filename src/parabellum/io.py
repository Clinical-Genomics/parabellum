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


# Test Scout parseing example
# IMPORTANT! Display all keys for a gene, some are not always present
# TODO: Make TSV
def parse_output(json_data: Dict):
    """
    Parse the output JSON.
    """
    for sample, genes in json_data.items():
        for gene, gene_info in genes.items():
            for key, val in gene_info.items():
                if (
                    isinstance(val, dict)
                    and {"value", "normal", "flag"}.issubset(val)
                    and val["flag"]
                ):
                    print(
                        f"Flagging region {gene} in sample {sample} because of key {key} (value: {val['value']}, normal: {val['normal']})"
                    )


def print_tsv(json_data: Dict) -> List[Tuple[str, str, str, float, float]]:
    """
    Print results in "TSV" format:

    Sample | Gene | Key | Value

    Where Value sometimes is a numeric, sometimes a list and sometimes a dict.
    """
    print("sample\tgene\tkey_is_flagged\tkey\tvalue_str")

    for sample, genes in json_data.items():
        for gene, gene_info in genes.items():
            key_is_flagged = False
            for key, val in gene_info.items():
                if isinstance(val, dict) and {"value", "normal", "flag"}.issubset(val):
                    value_str = stringify_value(val["value"])
                    # Flag in Scout
                    if val["flag"]:
                        key_is_flagged = True
                        logger.info(
                            f"Flagging region {gene} in sample {sample} because of key {key} (value: {val['value']}, normal: {val['normal']})"
                        )
                    print(f"{sample}\t{gene}\t{key_is_flagged}\t{key}\t{value_str}")
                else:
                    print(
                        f"{sample}\t{gene}\t{key_is_flagged}\t{key}\t{stringify_value(val)}"
                    )


def stringify_value(value) -> str | None:
    """
    Convert any value into a string for TSV.
    - Lists are joined by commas
    - Nested lists are flattened
    - Dicts are converted to key:value pairs, with nested lists flattened
    - None / empty list / empty dict return None
    """
    if value in (None, [], {}):
        return None

    if isinstance(value, (int, float, str)):
        return str(value)

    if isinstance(value, list):
        flat = []
        for v in value:
            if isinstance(v, list):
                flat.extend(map(str, v))
            else:
                flat.append(str(v))
        return ",".join(flat) if flat else None

    if isinstance(value, dict):
        items = []
        for k, v in value.items():
            if isinstance(v, dict):
                # inside nested dict, replace : with =
                # e.g. for {'CFH_hap1': {'type': 'deletion', 'breakpoint': [[196757557, 196760029], [196842234, 196844710]]}}
                sub_items = [
                    f"{subk}={stringify_value(subv)}" for subk, subv in v.items()
                ]
                items.append(f"{k}:{'|'.join(sub_items)}")
            else:
                items.append(f"{k}:{stringify_value(v)}")
        return ";".join(items) if items else None

    return str(value)
