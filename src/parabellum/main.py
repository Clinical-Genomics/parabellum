#!/usr/bin/env python3
import json
from pathlib import Path
from typing import List
import typer
import yaml
#from utils import OP_MAP
import operator
import sys

app = typer.Typer(
    rich_markup_mode="rich",
    invoke_without_command=True,
    pretty_exceptions_show_locals=False,
    add_completion=False,
    help="Call coverage drops over alleles in STR VCFs",
)

OP_MAP = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "!=": operator.ne,
    "==": operator.eq,
}

DEFAULT_SKIP_KEYS = (
    "sites_for_phasing,assembled_haplotypes,unique_supporting_reads,"
    "het_sites_not_used_in_phasing,nonunique_supporting_reads,read_details,"
    "haplotype_details,heterozygous_sites,homozygous_sites,final_haplotypes,flanking_summary,"
    "linked_haplotypes,alleles_raw,links_loose,directional_links,hap_links,alleles_full," #opn1lw
    "first_copies,last_copies,middle_copies," #opn1lw
    "sample_sex,"
    "smn1_read_number,smn2_read_number,smn2_del78_read_number," #sma
    "highest_total_cn," # Internal-use filed
    "gene_reads,pseudo_reads," # ncf1
    "del_read_number," # ikbkg
    "intergenic_depth," # strc
    "phasing_success,"
)

@app.command()
def main(
    input: List[Path] = typer.Option(
        ..., "--input", "-f", exists=True, file_okay=True, dir_okay=False,
        help="Input JSON file",
    ),
    sample: List[str] = typer.Option(
        ..., "--sample", "-s",
        help="Sample names corresponding to input JSON files",
    ),
    normal_yaml: Path = typer.Option(
    None,
    "--normal",
    "-n",
    exists=True,
    file_okay=True,
    dir_okay=False,
    help="Optional YAML file with normal values per gene"
    ),
    skip_keys: str = typer.Option(
        DEFAULT_SKIP_KEYS, help="Comma-separated keys to skip"
    ),
    genes: str = typer.Option(
        None,
        help="Optional comma-separated list of gene names to process"
    ),
):
    """
    Flatten Paraphase JSON fields, handle special cases like region_depth and final_haplotypes
    and merge into a multi-sample file.
    """
    check_equal_inputs_and_samples(input, sample)
    merged_data = merge_and_process(input, normal_yaml, sample, skip_keys, genes)
    json_str = json.dumps(merged_data, indent=2)
    #json_str = parse_output(merged_data)

    typer.echo(json_str)

def check_equal_inputs_and_samples(input_files: List[Path], sample_names: List[str]):
    if len(input_files) != len(sample_names):
        typer.echo(
            f"[error] Number of input files ({len(input_files)}) "
            f"does not match number of sample names ({len(sample_names)})",
            err=True
        )
        raise typer.Exit(code=1)

def load_yaml(file: Path):
    try:
        with file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        typer.echo(f"[error] Failed to read normal YAML: {e}", err=True)
        raise typer.Exit(code=1)
    return data

def load_json(file: Path):
    """Load one JSON file and process its contents."""
    try:
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        typer.echo(f"[error] Failed to read {file}: {e}", err=True)
        raise typer.Exit(code=1)
    return data

def merge_and_process(json_files: list[Path], normal: Path, sample_names: list[str], skip_keys: str, genes: str = None) -> dict:
    """
    Process and merge multiple JSON files.
    - skip_keys: comma-separated string of keys to skip
    - genes: optional comma-separated string of genes to keep
    """
    skip_keys_list = [k.strip() for k in skip_keys.split(",") if k.strip()]
    genes_list = [g.strip() for g in genes.split(",")] if genes else None
    normal_values = {}
    if normal:
        normal_values = load_yaml(normal)
    merged_data = {}
    for file, sample_name in zip(json_files, sample_names):
        paraphase_json = load_json(file)
        processed_json = process_paraphase_json(paraphase_json, normal_values, skip_keys_list, genes_list)
        merged_data[str(sample_name)] = processed_json

    return merged_data

def process_paraphase_json(data: dict, normal_values, skip_keys: List[str], genes_to_keep: List[str] = None) -> dict:
    """
    Process a single sample JSON structure, applying handlers and optionally filtering genes.
    """
    handlers = {
        "region_depth": handle_region_depth,
        "final_haplotypes": handle_final_haplotypes,
        "smn1_haplotypes": handle_final_haplotypes,
        "smn2_haplotypes": handle_final_haplotypes,
        "fusions_called": handle_fusions_called,
        "flanking_summary": handle_dict_to_list,
    }

    if genes_to_keep:
        # Keep only selected genes
        data = {gene: info for gene, info in data.items() if gene in genes_to_keep}

    return {gene: process_gene_info(gene, info, handlers, skip_keys, normal_values) for gene, info in data.items()}

def process_gene_info(gene_name, gene_info, handlers, skip_keys, normal_values):
    """
    Wrap simple values under a gene with {value, normal, flag}.
    normal_values: dict of gene -> key -> normal
    """
    processed = {}
    for key, value in gene_info.items():
        if key in skip_keys or value is None:
            continue

        if key in handlers:
            value = handlers[key](value)
        if normal_values and gene_name in normal_values and key in normal_values[gene_name]:
            rule = normal_values[gene_name][key]
            normal = normal_values[gene_name][key]["normal"]
            op = normal_values[gene_name][key]["op"]

            if isinstance(value, list) and (op != "==" and op != "!="):
                # For lists, only support equality check
                typer.echo(
                    f"[error] {gene_name} {key} is a list and op is {op}. Only '==' or '!=' is supported for lists.",
                    err=True
                )
                sys.exit(1)
            if op not in OP_MAP:
                typer.echo(
                    f"[error] {gene_name} {key} has unsupported operator '{op}'",
                    err=True
                )
                sys.exit(1)

            write_flag = False
            flag = False
            if op == "between":
                flag = not (rule["min"] <= value <= rule["max"])
                write_flag = True
            elif op in OP_MAP:
                flag = OP_MAP[op](value, normal)
                write_flag = True

            if(write_flag):
                processed[key] = {"value": value, "normal": normal, "flag": flag}
            else:
                processed[key] = value
        else:
            processed[key] = value

    return processed

def handle_region_depth(value):
    """
    Replace dict, e.g. { "median": 38.0, "percentile80": 45.2 } with median value.
    """
    return value['median']

def handle_final_haplotypes(value):
    """
    Replace a haplotypes dict , e.g.
    { "2111122111111111112111112111111111112111111111111111111111211": "smn1_smn1hap1" }
    with a list of haplotype values, e.g. ["smn1_smn1hap1"].
    """
    return list(value.values())

def handle_dict_to_list(value):
    """
    Convert dict to a list. E.g.
    "flanking_summary": {
        "f8_int22h2hap1": "region2-region2",
        "f8_int22h3hap1": "region3-region3",
        "f8_int22h1hap1": "region1-region1"
    }
    to [f8_int22h2hap1:region2-region2, f8_int22h3hap1:region3-region3, f8_int22h1hap1:region1-region1]
    """
    return [f"{k}:{v}" for k, v in value.items()]

def handle_fusions_called(value):
    """
    Remove sequence from fusions_called dict.
    """
    return {
        hap: {k: v for k, v in hap_val.items() if k != "sequence"}
        for hap, hap_val in value.items()
    }

# Test Scout parseing example
# IMPORTANT! Display all keys for a gene, some are not always present
def parse_output(json_data: dict):
    """
    Parse the output JSON.
    """
    for sample, genes in json_data.items():
        for gene, gene_info in genes.items():
            for key, val in gene_info.items():
                if isinstance(val, dict) and "value" in val and "normal" in val and "flag" in val and val["flag"]:
                    print(f"Flagging region {gene} in sample {sample} because of key {key} (value: {val['value']}, normal: {val['normal']})")


# TODO: Keep the original get tags functions in a utils section
# Make one main app function to call, and one to get info

# TODO: Print TSV so we can do some tables

if __name__ == "__main__":
    app()
