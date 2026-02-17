from parabellum.rules_engine import eval_when


def test_not_empty_operator_on_dict_and_list():
    gene_info = {
        "fusions_called": {"some": "value"},
        "sv_called": [],
        "notes": "",
    }

    # Dict that is not {} should satisfy not_empty
    assert eval_when(gene_info, {"fusions_called": {"not_empty": True}}) is True

    # Empty list should NOT satisfy not_empty
    assert eval_when(gene_info, {"sv_called": {"not_empty": True}}) is False

    # Empty string should NOT satisfy not_empty
    assert eval_when(gene_info, {"notes": {"not_empty": True}}) is False

