from pathlib import Path
import yaml
import json
import logging
import sys
from .exceptions import JSONLoadError, YAMLLoadError
from typing import Dict, List, Tuple

logger = logging.getLogger("paraphase")
logger.setLevel(logging.INFO)

# Create a single logger
logger = logging.getLogger("paraphase")
logger.setLevel(logging.DEBUG)  # capture all levels


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "INFO": "\033[93m",  # yellow
        "WARNING": "\033[91m",  # red
        "ERROR": "\033[91m",  # red
        "DEBUG": "\033[94m",  # blue
        "RESET": "\033[0m",
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        message = super().format(record)
        return f"{color}{message}{self.COLORS['RESET']}"


# Single handler for stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(ColoredFormatter("%(levelname)s: %(message)s"))

# Remove default handlers if any, then add ours
if logger.hasHandlers():
    logger.handlers.clear()
logger.addHandler(handler)


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
    flagged = []

    for sample, genes in json_data.items():
        for gene, gene_info in genes.items():
            for key, val in gene_info.items():
                if isinstance(val, dict) and {"value", "normal", "flag"}.issubset(val):
                    value_str = stringify_value(val["value"])
                    print(f"{sample}\t{gene}\t{key}\t{value_str}")

                    # Flag in Scout
                    if val["flag"]:
                        logger.info(
                            f"Flagging region {gene} in sample {sample} because of key {key} (value: {val["value"]}, normal: {val["normal"]})"
                        )
                else:
                    print(f"{sample}\t{gene}\t{key}\t{stringify_value(val)}")

    return flagged


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
                sub_items = [f"{subk}={stringify_value(subv)}" for subk, subv in v.items()]
                items.append(f"{k}:{'|'.join(sub_items)}")
            else:
                items.append(f"{k}:{stringify_value(v)}")
        return ";".join(items) if items else None

    return str(value)
