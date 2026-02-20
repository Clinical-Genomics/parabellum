from parabellum.io import print_tsv


def test_print_tsv_uses_gene_status_and_hides_status_row(capsys):
    json_data = {
        "S1": {
            "smn1": {
                "status": "pathological",
                "region_depth": 44.0,
                "status_matches": [{"status": "pathological", "rule_index": 0}],
            },
            "CFH": {
                # No status defined for this gene -> should be reported as 'unknown'
                "region_depth": 41.0,
            },
        }
    }

    print_tsv(json_data)
    captured = capsys.readouterr().out.strip().splitlines()

    # Header
    assert captured[0] == "sample\tlocus\tstatus\tkey\tvalue"

    # Rows for smn1: only the data key, not the status/status_matches keys
    assert "S1\tsmn1\tpathological\tregion_depth\t44.0" in captured
    assert not any("status_matches" in line for line in captured)
    assert not any("\tsmn1\tpathological\tstatus\t" in line for line in captured)

    # CFH has no status, so should be 'unknown'
    assert "S1\tCFH\tunknown\tregion_depth\t41.0" in captured
