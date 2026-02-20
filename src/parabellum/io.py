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
    print("sample\tgene\tstatus\tkey\tvalue")

    for sample, genes in json_data.items():
        for gene, gene_info in genes.items():
            # Gene-level status comes from the rules engine; if no rules were
            # defined or no status was set, report it as "unknown"
            gene_status = gene_info.get("status")
            if not isinstance(gene_status, str):
                gene_status = "unknown"

            for key, val in gene_info.items():
                # Do not emit the per-gene status or rule-match metadata as separate rows
                if key in {"status", "status_matches"}:
                    continue

                value_str = stringify_value(val)

                print(f"{sample}\t{gene}\t{gene_status}\t{key}\t{value_str}")


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
                if inner := [str(item) for item in val if item is not None]:
                    flat.append(",".join(inner))
            elif item is not None:
                flat.append(str(item))
        return ",".join(flat) if flat else None

    if isinstance(content, dict):
        flattened_items = []
        for key, value in content.items():
            if value in (None, [], {}):
                continue
            if isinstance(value, dict):
                # nested dicts: subkey=subvalue
                if sub_items := [
                    f"{subkey}={stringify_value(subvalue)}"
                    for subkey, subvalue in value.items()
                    if stringify_value(subvalue) is not None
                ]:
                    flattened_items.append(f"{key}:{'|'.join(sub_items)}")
            else:
                content_string = stringify_value(content)
                if content_string is not None:
                    items.append(f"{key}:{content_string}")
        return ";".join(flattened_items) if flattened_items else None

    return str(content)
