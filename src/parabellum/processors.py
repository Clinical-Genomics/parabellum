from .constants import OP_MAP
from .exceptions import InvalidOperatorError, ListOpNotSupportedError
from .config import ProcessingConfig


def process_paraphase_json(data: dict, config: ProcessingConfig) -> dict:
    """
    Process a single sample JSON structure, applying handlers and optionally filtering genes.
    """
    skip_keys = config.skip_keys
    genes_to_keep = config.genes_list
    normal_values = config.normal_values

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

    return {
        gene: process_gene_info(gene, info, handlers, skip_keys, normal_values)
        for gene, info in data.items()
    }


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
        if (
            normal_values
            and gene_name in normal_values
            and key in normal_values[gene_name]
        ):
            rule = normal_values[gene_name][key]
            normal = normal_values[gene_name][key]["normal"]
            op = normal_values[gene_name][key]["op"]

            if isinstance(value, list) and op not in ["==", "!=", "not_in"]:
                raise ListOpNotSupportedError(
                    f"{gene_name} {key} is a list and op is {op}. Only '==', '!=' or 'not_in' is supported for lists."
                )
            if op not in OP_MAP:
                raise InvalidOperatorError(
                    f"{gene_name} {key} has unsupported operator '{op}'."
                )

            write_flag = False
            flag = False
            if op == "between":
                flag = not (rule["min"] <= value <= rule["max"])
                write_flag = True
            if op == "not_in":
                flag = value not in normal
                write_flag = True
            elif op in OP_MAP:
                flag = OP_MAP[op](value, normal)
                write_flag = True

            if write_flag:
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
    return value["median"]


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
