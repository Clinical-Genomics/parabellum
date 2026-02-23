from pathlib import Path
from typing import List
from .processors import process_paraphase_json
from .exceptions import InputMismatchError
from .config import ProcessingConfig


def merge_and_process(
    json_dicts: list[dict], sample_names: list[str], config: ProcessingConfig
) -> dict:
    """
    Merge multiple JSON files with sample_names as keys.
    """
    merged_data = {}
    for data, sample_name in zip(json_dicts, sample_names):
        processed_json = process_paraphase_json(data, config)
        merged_data[str(sample_name)] = processed_json
    return merged_data


def assert_equal_inputs_and_samples(input_files: List[Path], sample_names: List[str]):
    if len(input_files) != len(sample_names):
        raise InputMismatchError(
            f"Number of input files ({len(input_files)}) does not match "
            f"number of sample names ({len(sample_names)})"
        )
