#!/usr/bin/env python3
import json
from pathlib import Path
from typing import List, Optional
import typer
from .constants import DEFAULT_SKIP_KEYS
from .pipeline import merge_and_process, assert_equal_inputs_and_samples
from .io import load_json, load_yaml, print_tsv
from .exceptions import InputMismatchError
from .config import ProcessingConfig

app = typer.Typer(
    rich_markup_mode="rich",
    invoke_without_command=True,
    pretty_exceptions_show_locals=False,
    add_completion=False,
    help="Call coverage drops over alleles in STR VCFs",
)


@app.command()
def main(
    input: List[Path] = typer.Option(
        ...,
        "--input",
        "-f",
        exists=True,
        file_okay=True,
        dir_okay=False,
        help="Input JSON files (can be multiple)",
    ),
    sample: List[str] = typer.Option(
        ...,
        "--sample",
        "-s",
        help="Sample names corresponding to input JSON files",
    ),
    rules_yaml: Optional[Path] = typer.Option(
        None,
        "--rules",
        "-r",
        exists=True,
        file_okay=True,
        dir_okay=False,
        help="Optional YAML file with per-gene classification rules (adds 'status' fields)",
    ),
    skip_keys: str = typer.Option(
        None, help="Comma-separated keys to skip (e.g. region_depth,final_haplotypes)"
    ),
    genes: Optional[str] = typer.Option(
        None, help="Optional comma-separated list of gene names to process"
    ),
    output_format: str = typer.Option(
        "json", "--output-format", "-o", help="Output format: 'json' (default) or 'tsv'"
    ),
):
    """
    Parse paraphase JSONs.
    """
    try:
        # Parse and validate parameters
        skip_keys_list = (
            [k.strip() for k in skip_keys.split(",")]
            if skip_keys
            else list(DEFAULT_SKIP_KEYS)
        )
        # TODO: Genes should not be case-sensitive
        genes_list = [g.strip() for g in genes.split(",")] if genes else None
        assert_equal_inputs_and_samples(input, sample)

        # Get input files
        rules = load_yaml(rules_yaml) if rules_yaml else None
        json_data_list = [load_json(f) for f in input]

        config = ProcessingConfig(
            skip_keys=set(skip_keys_list),
            genes_list=genes_list,
            rules=rules,
        )

        merged_data = merge_and_process(json_data_list, sample, config)

        if output_format.lower() == "tsv":
            print_tsv(merged_data)
        else:
            typer.echo(json.dumps(merged_data, indent=2))
    except InputMismatchError as e:
        typer.echo(f"[error] {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
