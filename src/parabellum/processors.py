from .config import ProcessingConfig
from .rules_engine import evaluate_gene_rules


def process_paraphase_json(data: dict, config: ProcessingConfig) -> dict:
    """
    Process a single sample JSON structure, applying handlers and optionally filtering genes.
    """
    skip_keys = config.skip_keys
    genes_to_keep = (
        {g.lower() for g in config.genes_list} if config.genes_list else None
    )

    handlers = {
        "region_depth": handle_region_depth,
        "final_haplotypes": handle_final_haplotypes,
        "smn_del78_haplotypes": handle_final_haplotypes,
        "smn2_del78_haplotypes": handle_final_haplotypes,
        "smn1_haplotypes": handle_final_haplotypes,
        "smn2_haplotypes": handle_final_haplotypes,
        "fusions_called": handle_fusions_called,
        "flanking_summary": handle_dict_to_list,
    }

    if genes_to_keep:
        # Keep only selected genes (case-insensitive)
        data = {
            gene: info
            for gene, info in data.items()
            if gene.lower() in genes_to_keep
        }

    out = {}
    for gene, info in data.items():
        processed = process_gene_info(gene, info, handlers, skip_keys)

        # Optional, per-gene classification rules
        if config.rules:
            status, matches = evaluate_gene_rules(gene, processed, config.rules)
            if status is not None:
                processed["status"] = status
                # Keep a lightweight trace in json
                if matches:
                    processed["status_matches"] = [
                        {
                            "status": m.status,
                            "rule_index": m.rule_index,
                            "reason": m.rule.get("reason"),
                            "rule": m.rule,
                        }
                        for m in matches
                    ]

        out[gene] = processed

    return out


def process_gene_info(gene_name, gene_info, handlers, skip_keys):
    """
    Apply per-key handlers and drop skipped/None values under a gene.
    """
    processed = {}
    for key, value in gene_info.items():
        if key in skip_keys or value is None:
            continue

        if key in handlers:
            value = handlers[key](value)

        # TODO: Stringify values here instead, for both JSON and TSV output?
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
