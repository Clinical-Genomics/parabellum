import json
from collections import Counter

def main():
    with open('data/assuringredbird_merged.json', 'r') as f:
        paraphase = json.load(f)

    skip_keys = [
        "sites_for_phasing",
        "assembled_haplotypes",
        "unique_supporting_reads",
        "het_sites_not_used_in_phasing",
        "nonunique_supporting_reads",
        "read_details",
        "haplotype_details", # Probably too many variants. For e.g. rccx 'hap_variants' contains a subset of identifying variants
        "heterozygous_sites",
        "homozygous_sites",
    ]

    for sample_id, sample_info in paraphase.items():
        for gene, gene_info in sample_info.items():
            for key, value in gene_info.items():
                if key == "haplotype_details":
                    print(f"{sample_id}\t{gene}\t{key}\t{value}")

     # Print summary of all keys
    print("\n--- Gene count per sample ---")
    genes_per_sample = count_genes(paraphase) / count_samples(paraphase)
    print(f"{genes_per_sample:.0f}")

     # Print summary of all keys
    print("\n--- Key counts per sample ---")
    for key, count in count_all_keys_occurance(paraphase).most_common():
        print(f"{key}: {count / count_samples(paraphase):.0f}")

def count_genes(json_data):
    """Return total number of gene entries across all samples."""
    return sum(len(sample_info) for sample_info in json_data.values())

def count_samples(json_data):
    """Return total number of gene entries across all samples."""
    return len(json_data)

def count_all_keys_occurance(json_data):
    """Count occurrences of each key across all genes and samples."""
    key_counter = Counter()
    for sample_id, sample_info in json_data.items():
        for gene, gene_info in sample_info.items():
            for key, value in gene_info.items():
                key_counter[key] += 1
    return key_counter

def parse_final_haplotypes(final_haplotypes):
    """Parse the final_haplotypes into a list of haplotype names"""
    if not final_haplotypes:
        return []
    return list(final_haplotypes.values())

def genes_missing_key(json_data, target_key):
    """Return a list of (sample_id, gene) tuples where the key is missing."""
    missing = []
    for sample_id, sample_info in json_data.items():
        for gene, gene_info in sample_info.items():
            if target_key not in gene_info:
                missing.append((sample_id, gene))
    return missing

def check_total_cn_difference(json_data):
    differences = []
    for sample_id, sample_info in json_data.items():
        for gene, gene_info in sample_info.items():
            total_cn = gene_info.get("alleles_final")
            highest_total_cn = gene_info.get("linked_haplotypes")
            if total_cn is not None and highest_total_cn is not None:
                if total_cn != highest_total_cn:
                    differences.append((sample_id, gene, total_cn, highest_total_cn))
    return differences

if __name__ == "__main__":
    main()

