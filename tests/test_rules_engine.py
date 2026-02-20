from parabellum.rules_engine import evaluate_gene_rules, eval_when


def test_eval_when_map_means_and_across_keys():
    gene_info = {"smn1_cn": 0, "smn2_cn": 5, "x": 1}

    # Multiple keys means AND across leaves
    assert eval_when(gene_info, {"smn1_cn": 0, "smn2_cn": {">=": 4}}) is True
    assert eval_when(gene_info, {"smn1_cn": 1, "smn2_cn": {">=": 4}}) is False


def test_evaluate_gene_rules_picks_most_severe_by_status_order_and_returns_matches():
    rules = {
        "smn1": {
            "default_status": "normal",
            "status_order": ["normal", "intermediate", "pathological"],
            "rules": [
                {
                    "status": "intermediate",
                    # AND across keys in the mapping
                    "when": {"smn1_cn": 0, "smn2_cn": {">=": 4}},
                    "reason": "SMN1 deleted but SMN2 high",
                },
                {
                    "status": "pathological",
                    "when": {"smn1_cn": {"<": 2}},
                    "reason": "SMN1 copy number low",
                },
            ],
        }
    }

    status, matches = evaluate_gene_rules("smn1", {"smn1_cn": 0, "smn2_cn": 5}, rules)
    assert status == "pathological"  # both match; pick most severe
    assert {m.status for m in matches} == {"intermediate", "pathological"}


def test_eval_when_field_reference():
    """Compare a field to another field's value (e.g. exon depth < genome_depth)."""
    gene_info = {"exon1_to_exon22_depth": 13.0, "genome_depth": 24.0}
    assert (
        eval_when(gene_info, {"exon1_to_exon22_depth": {"<": "genome_depth"}}) is True
    )
    gene_info_high = {"exon1_to_exon22_depth": 30.0, "genome_depth": 24.0}
    assert (
        eval_when(gene_info_high, {"exon1_to_exon22_depth": {"<": "genome_depth"}})
        is False
    )


def test_evaluate_gene_rules_default_status_when_no_match():
    rules = {
        "smn1": {
            "default_status": "normal",
            "status_order": ["normal", "intermediate", "pathological"],
            "rules": [
                {"status": "pathological", "when": {"smn1_cn": {"<": 2}}},
            ],
        }
    }
    status, matches = evaluate_gene_rules("smn1", {"smn1_cn": 2}, rules)
    assert status == "normal"
    assert matches == []
