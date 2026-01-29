import pytest

"""Basic tests for parabellum."""


def test_process_paraphase_json():
    from parabellum.processors import process_paraphase_json
    from parabellum.config import ProcessingConfig

    input_data = {
        "smn1": {
            "region_depth": {"median": 44.0, "percentile80": 48.0},
            "final_haplotypes": {
                "x22222122222221111111111": "smn1_smn2hap1",
                "x22222222221112222222222": "smn1_smn2hap2",
            },
        },
        "F8": {
            "flanking_summary": {
                "f8_int22h2hap1": "region2-region2",
                "f8_int22h3hap1": "-region3",
                "f8_int22h2hap2": "-region2",
                "f8_int22h1hap1": "region1-region1",
                "f8_int22h1hap2": "region1-region1",
            }
        },
    }

    config = ProcessingConfig(
        skip_keys=[],
        genes_list=["smn1", "F8"],
        normal_values={
            "smn1": {
                "region_depth": {"op": "between", "min": 30, "max": 60},
            }
        },
    )

    expected_output = {
        "smn1": {
            "region_depth": {
                "value": 44.0,
                "normal": "min(30) - max(60)",
                "flag": True,
            },
            "final_haplotypes": ["smn1_smn2hap1", "smn1_smn2hap2"],
        },
        "F8": {
            "flanking_summary": [
                "f8_int22h2hap1:region2-region2",
                "f8_int22h3hap1:-region3",
                "f8_int22h2hap2:-region2",
                "f8_int22h1hap1:region1-region1",
                "f8_int22h1hap2:region1-region1",
            ]
        },
    }
    assert process_paraphase_json(input_data, config) == expected_output


def test_process_gene_info():
    from parabellum.processors import process_gene_info
    from parabellum.processors import (
        handle_region_depth,
        handle_final_haplotypes,
    )

    handlers = {
        "region_depth": handle_region_depth,
        "final_haplotypes": handle_final_haplotypes,
    }
    gene_name = "smn1"
    gene_info = {
        "region_depth": {"median": 44.0, "percentile80": 48.0},
        "final_haplotypes": {
            "x22222122222221111111111": "smn1_smn2hap1",
            "x22222222221112222222222": "smn1_smn2hap2",
        },
    }
    skip_keys = "final_haplotypes"
    normal_values = {"smn1": {"region_depth": {"op": "between", "min": 30, "max": 60}}}
    expected_output = {
        "region_depth": {"value": 44.0, "normal": "min(30) - max(60)", "flag": True}
    }
    assert (
        process_gene_info(gene_name, gene_info, handlers, skip_keys, normal_values)
        == expected_output
    )


def test_process_gene_info_invalid_list_operator():
    from parabellum.exceptions import ListOpNotSupportedError
    from parabellum.processors import process_gene_info
    from parabellum.processors import (
        handle_region_depth,
        handle_final_haplotypes,
    )

    handlers = {
        "region_depth": handle_region_depth,
        "final_haplotypes": handle_final_haplotypes,
    }
    gene_name = "smn1"
    gene_info = {
        "region_depth": {"median": 44.0, "percentile80": 48.0},
        "final_haplotypes": {
            "x22222122222221111111111": "smn1_smn2hap1",
            "x22222222221112222222222": "smn1_smn2hap2",
        },
    }
    skip_keys = "region_depth"
    normal_values = {
        "smn1": {"final_haplotypes": {"op": "between", "min": 30, "max": 60}}
    }
    with pytest.raises(ListOpNotSupportedError):
        process_gene_info(
            gene_name,
            gene_info,
            handlers,
            skip_keys,
            normal_values,
        )


def test_process_gene_info_invalid_operator():
    from parabellum.exceptions import InvalidOperatorError
    from parabellum.processors import process_gene_info
    from parabellum.processors import (
        handle_region_depth,
        handle_final_haplotypes,
    )

    handlers = {
        "region_depth": handle_region_depth,
        "final_haplotypes": handle_final_haplotypes,
    }
    gene_name = "smn1"
    gene_info = {
        "region_depth": {"median": 44.0, "percentile80": 48.0},
        "final_haplotypes": {
            "x22222122222221111111111": "smn1_smn2hap1",
            "x22222222221112222222222": "smn1_smn2hap2",
        },
    }
    skip_keys = "final_haplotypes"
    normal_values = {"smn1": {"region_depth": {"op": "not_an_operator", "normal": 50}}}
    with pytest.raises(InvalidOperatorError):
        process_gene_info(
            gene_name,
            gene_info,
            handlers,
            skip_keys,
            normal_values,
        )


def test_process_gene_info_invalid_key():
    from parabellum.processors import process_gene_info
    from parabellum.processors import (
        handle_region_depth,
        handle_final_haplotypes,
    )

    handlers = {
        "region_depth": handle_region_depth,
        "final_haplotypes": handle_final_haplotypes,
    }
    gene_name = "smn1"
    gene_info = {
        "region_depth": {"median": 44.0, "percentile80": 48.0},
        "final_haplotypes": {
            "x22222122222221111111111": "smn1_smn2hap1",
            "x22222222221112222222222": "smn1_smn2hap2",
        },
    }
    skip_keys = "final_haplotypes"
    normal_values = {
        "smn1": {"region_depth": {"op": "==", "normal_key": "non_existent_key"}}
    }
    with pytest.raises(KeyError):
        process_gene_info(
            gene_name,
            gene_info,
            handlers,
            skip_keys,
            normal_values,
        )


def test_process_gene_info_valid_key():
    from parabellum.processors import process_gene_info
    from parabellum.processors import (
        handle_region_depth,
        handle_final_haplotypes,
    )

    handlers = {
        "region_depth": handle_region_depth,
        "final_haplotypes": handle_final_haplotypes,
    }
    gene_name = "smn1"
    gene_info = {
        "region_depth": {"median": 44.0, "percentile80": 48.0},
        "final_haplotypes": {
            "x22222122222221111111111": "smn1_smn2hap1",
            "x22222222221112222222222": "smn1_smn2hap2",
        },
        "genome_depth": 45.0,
    }
    skip_keys = "final_haplotypes,genome_depth"
    normal_values = {
        "smn1": {"region_depth": {"op": "<", "normal_key": "genome_depth"}}
    }
    expected_output = {"region_depth": {"value": 44.0, "normal": 45.0, "flag": True}}
    assert (
        process_gene_info(gene_name, gene_info, handlers, skip_keys, normal_values)
        == expected_output
    )


def test_process_gene_info_invalid_normal():
    from parabellum.processors import process_gene_info
    from parabellum.processors import (
        handle_region_depth,
        handle_final_haplotypes,
    )

    handlers = {
        "region_depth": handle_region_depth,
        "final_haplotypes": handle_final_haplotypes,
    }
    gene_name = "smn1"
    gene_info = {
        "region_depth": {"median": 44.0, "percentile80": 48.0},
        "final_haplotypes": {
            "x22222122222221111111111": "smn1_smn2hap1",
            "x22222222221112222222222": "smn1_smn2hap2",
        },
        "genome_depth": 45.0,
    }
    skip_keys = "final_haplotypes,genome_depth"
    normal_values = {"smn1": {"region_depth": {"op": "<", "normal_notkey": 45.0}}}
    with pytest.raises(ValueError):
        process_gene_info(
            gene_name,
            gene_info,
            handlers,
            skip_keys,
            normal_values,
        )


def test_process_gene_info_numeric_and_non_numeric():
    from parabellum.processors import process_gene_info
    from parabellum.processors import (
        handle_region_depth,
        handle_final_haplotypes,
    )

    handlers = {
        "region_depth": handle_region_depth,
        "final_haplotypes": handle_final_haplotypes,
    }
    gene_name = "smn1"
    gene_info = {
        "region_depth": {"median": 44.0, "percentile80": 48.0},
        "final_haplotypes": {
            "x22222122222221111111111": "smn1_smn2hap1",
            "x22222222221112222222222": "smn1_smn2hap2",
        },
        "genome_depth": 45.0,
    }
    skip_keys = "final_haplotypes,genome_depth"
    normal_values = {"smn1": {"region_depth": {"op": "<", "normal": "not_a_number"}}}
    with pytest.raises(TypeError):
        process_gene_info(
            gene_name,
            gene_info,
            handlers,
            skip_keys,
            normal_values,
        )


def test_process_gene_info_not_between_operator():
    from parabellum.processors import process_gene_info
    from parabellum.processors import (
        handle_region_depth,
        handle_final_haplotypes,
    )

    handlers = {
        "region_depth": handle_region_depth,
        "final_haplotypes": handle_final_haplotypes,
    }
    gene_name = "smn1"
    gene_info = {
        "region_depth": {"median": 44.0, "percentile80": 48.0},
        "final_haplotypes": {
            "x22222122222221111111111": "smn1_smn2hap1",
            "x22222222221112222222222": "smn1_smn2hap2",
        },
        "genome_depth": 45.0,
    }
    skip_keys = "final_haplotypes,genome_depth"
    normal_values = {
        "smn1": {"region_depth": {"op": "not_between", "min": 30, "max": 60}}
    }
    expected_output = {
        "region_depth": {"flag": False, "normal": "min(30) - max(60)", "value": 44.0}
    }
    assert (
        process_gene_info(gene_name, gene_info, handlers, skip_keys, normal_values)
        == expected_output
    )


def test_process_gene_info_not_in_operator():
    from parabellum.processors import process_gene_info
    from parabellum.processors import (
        handle_region_depth,
        handle_final_haplotypes,
    )

    handlers = {
        "region_depth": handle_region_depth,
        "final_haplotypes": handle_final_haplotypes,
    }
    gene_name = "smn1"
    gene_info = {
        "region_depth": {"median": 44.0, "percentile80": 48.0},
        "final_haplotypes": {
            "x22222122222221111111111": "smn1_smn2hap1",
            "x22222222221112222222222": "smn1_smn2hap2",
        },
        "genome_depth": 45.0,
    }
    skip_keys = "genome_depth,region_depth"
    normal_values = {
        "smn1": {"final_haplotypes": {"op": "not_in", "normal": ["smn1_smn2hap1"]}}
    }
    expected_output = {
        "final_haplotypes": {
            "flag": True,
            "normal": ["smn1_smn2hap1"],
            "value": ["smn1_smn2hap1", "smn1_smn2hap2"],
        }
    }
    assert (
        process_gene_info(gene_name, gene_info, handlers, skip_keys, normal_values)
        == expected_output
    )


def test_process_gene_info_equals_operator():
    from parabellum.processors import process_gene_info
    from parabellum.processors import (
        handle_region_depth,
        handle_final_haplotypes,
    )

    handlers = {
        "region_depth": handle_region_depth,
        "final_haplotypes": handle_final_haplotypes,
    }
    gene_name = "smn1"
    gene_info = {
        "region_depth": {"median": 44.0, "percentile80": 48.0},
        "final_haplotypes": {
            "x22222122222221111111111": "smn1_smn2hap1",
            "x22222222221112222222222": "smn1_smn2hap2",
        },
        "genome_depth": 45.0,
    }
    skip_keys = "final_haplotypes,region_depth"
    normal_values = {"smn1": {"genome_depth": {"op": "==", "normal": 45}}}
    expected_output = {"genome_depth": {"flag": True, "normal": 45, "value": 45.0}}
    assert (
        process_gene_info(gene_name, gene_info, handlers, skip_keys, normal_values)
        == expected_output
    )


def test_process_gene_info_valid_operator():
    from parabellum.processors import process_gene_info
    from parabellum.processors import (
        handle_region_depth,
        handle_final_haplotypes,
    )

    handlers = {
        "region_depth": handle_region_depth,
        "final_haplotypes": handle_final_haplotypes,
    }
    gene_name = "smn1"
    gene_info = {
        "region_depth": {"median": 44.0, "percentile80": 48.0},
        "final_haplotypes": {
            "x22222122222221111111111": "smn1_smn2hap1",
            "x22222222221112222222222": "smn1_smn2hap2",
        },
        "genome_depth": 45.0,
    }
    skip_keys = "final_haplotypes,genome_depth"
    normal_values = {"smn1": {"region_depth": {"op": "<", "normal": 45.0}}}
    expected_output = {"region_depth": {"value": 44.0, "normal": 45.0, "flag": True}}
    print(process_gene_info(gene_name, gene_info, handlers, skip_keys, normal_values))
    assert (
        process_gene_info(gene_name, gene_info, handlers, skip_keys, normal_values)
        == expected_output
    )


def test_handle_region_depth():
    from parabellum.processors import handle_region_depth

    input_data = {"median": 44.0, "percentile80": 48.0}

    expected_output = 44.0
    assert handle_region_depth(input_data) == expected_output


def test_handle_final_haplotypes():
    from parabellum.processors import handle_final_haplotypes

    input_data = {
        "x22222122222221111111111": "smn1_smn2hap1",
        "x22222222221112222222222": "smn1_smn2hap2",
    }

    expected_output = ["smn1_smn2hap1", "smn1_smn2hap2"]
    assert handle_final_haplotypes(input_data) == expected_output


def test_handle_dict_to_list():
    from parabellum.processors import handle_dict_to_list

    input_data = {
        "f8_int22h2hap1": "region2-region2",
        "f8_int22h3hap1": "-region3",
        "f8_int22h2hap2": "-region2",
        "f8_int22h1hap1": "region1-region1",
        "f8_int22h1hap2": "region1-region1",
    }

    expected_output = [
        "f8_int22h2hap1:region2-region2",
        "f8_int22h3hap1:-region3",
        "f8_int22h2hap2:-region2",
        "f8_int22h1hap1:region1-region1",
        "f8_int22h1hap2:region1-region1",
    ]
    assert handle_dict_to_list(input_data) == expected_output


def test_handle_fusions_called():
    from parabellum.processors import handle_fusions_called

    input_data = {
        "CFH_hap1": {
            "type": "deletion",
            "sequence": "11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111122222222222222221112222122222222222222222222221112222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222",
            "breakpoint": [[196757557, 196760029], [196842234, 196844710]],
        }
    }

    expected_output = {
        "CFH_hap1": {
            "type": "deletion",
            "breakpoint": [[196757557, 196760029], [196842234, 196844710]],
        }
    }
    assert handle_fusions_called(input_data) == expected_output
