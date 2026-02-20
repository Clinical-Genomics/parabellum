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


def print_tsv(json_data: Dict) -> List[Tuple[str, str, str, float, float]]:
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


def stringify_value(value) -> str | None:
    """
    Flatten nested dicts/lists for TSV output.
    - Skip empty or None values.
    - Top-level dict: key:value
    - Nested dicts: key=subkey=subvalue
    - Lists: joined by commas
    """
    if value in (None, [], {}):
        return None

    if isinstance(value, (int, float, str)):
        return str(value)

    if isinstance(value, list):
        flat = []
        for v in value:
            if isinstance(v, list):
                if inner := [str(i) for i in v if i is not None]:
                    flat.append(",".join(inner))
            elif v is not None:
                flat.append(str(v))
        return ",".join(flat) if flat else None

    if isinstance(value, dict):
        items = []
        for k, v in value.items():
            if v in (None, [], {}):
                continue
            if isinstance(v, dict):
                # nested dicts: subkey=subvalue
                sub_items = [
                    f"{subk}={stringify_value(subv)}"
                    for subk, subv in v.items()
                    if stringify_value(subv) is not None
                ]
                if sub_items:
                    items.append(f"{k}:{'|'.join(sub_items)}")
            else:
                v_str = stringify_value(v)
                if v_str is not None:
                    items.append(f"{k}:{v_str}")
        return ";".join(items) if items else None

    return str(value)
