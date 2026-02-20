from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import operator

NUMERIC_FUNCTIONS = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}


@dataclass(frozen=True)
class RuleMatch:
    status: str
    rule_index: int
    rule: Dict[str, Any]  # full rule dict: at least "status" and "when"


def _get_path_value(object: Any, path: str) -> Any:
    """
    Get a possibly nested value from dict-like structures.
    Supports dot-paths like 'fusions_called.value.CFH_hap1.type'.
    """
    current = object
    for part in path.split("."):
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _coerce_numeric(x: Any) -> Optional[float]:
    """
    Coerce a value to a float.
    """
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        try:
            return float(x)
        except ValueError:
            return None
    return None


def _op_not_empty(actual: Any, _: Any) -> bool:
    return actual not in (None, "", [], {})


def _op_eq(actual: Any, expected: Any) -> bool:
    return actual == expected


def _op_ne(actual: Any, expected: Any) -> bool:
    return actual != expected


def _op_in(actual: Any, expected: Any) -> bool:
    return actual in (expected or [])


def _op_not_in(actual: Any, expected: Any) -> bool:
    return actual not in (expected or [])


def _op_contains(actual: Any, expected: Any) -> bool:
    return expected in (actual or [])


def _op_not_contains(actual: Any, expected: Any) -> bool:
    return expected not in (actual or [])


def _numeric_handler(
    function: Callable[[float, float], bool],
) -> Callable[[Any, Any], bool]:
    """
    Wrap a numeric function to coerce actual and expected values to floats.
    """

    def handler(actual: Any, expected: Any) -> bool:
        actual = _coerce_numeric(actual)
        expected = _coerce_numeric(expected)
        if actual is None or expected is None:
            return False
        return function(actual, expected)

    return handler


# Numeric handlers are functions that take two floats and return a boolean.
NUMERIC_HANDLERS = {
    operator: _numeric_handler(function)
    for operator, function in NUMERIC_FUNCTIONS.items()
}

# Operator handlers are functions that take two values and return a boolean.
OPERATOR_HANDLERS = {
    "not_empty": _op_not_empty,
    "==": _op_eq,
    "!=": _op_ne,
    "in": _op_in,
    "not_in": _op_not_in,
    "contains": _op_contains,
    "not_contains": _op_not_contains,
    **NUMERIC_HANDLERS,
}


def _apply_operator(actual: Any, operator: str, expected: Any) -> bool:
    """
    Apply an operator to two values.
    """
    try:
        handler = OPERATOR_HANDLERS[operator]
    except KeyError:
        raise ValueError(f"Unsupported operator in rules: {operator}")

    return handler(actual, expected)


def _eval_leaf(gene_info: Dict[str, Any], leaf: Dict[str, Any]) -> bool:
    """
    Leaf condition formats supported:
    - { key: scalar } -> equality
    - { key: {">=": 4} } -> single operator
    """
    if len(leaf) != 1:
        # Avoid ambiguous leaf dicts; require single key.
        return False

    key, spec = next(iter(leaf.items()))
    actual = _get_path_value(gene_info, key)

    if isinstance(spec, dict):
        # Exactly one operator per key to keep rules simple.
        if len(spec) != 1:
            raise ValueError(
                f"Multiple operators for the same key are not supported: {leaf!r}"
            )
        op, expected = next(iter(spec.items()))
        # Resolve field reference: if expected is a string that is a key in
        # gene_info, compare against that field's value (e.g. "<": genome_depth).
        if isinstance(expected, str) and expected in gene_info:
            expected = _get_path_value(gene_info, expected)
        return _apply_operator(actual, op, expected)
    else:
        expected = spec
        if isinstance(expected, str) and expected in gene_info:
            expected = _get_path_value(gene_info, expected)
        return _apply_operator(actual, "==", expected)


def eval_when(gene_info: Dict[str, Any], expression: Any) -> bool:
    """
    Evaluate a 'when' expression.

    Supported form:
    - {key: value} or {key: {op: value}}
      Multiple keys in the same mapping are combined with AND, e.g.:
        {k1: 1, k2: {">=": 4}} means (k1 == 1 AND k2 >= 4).
    """
    if expression is None:
        return True

    if isinstance(expression, dict):
        # Multiple keys -> AND of leaves
        if len(expression) > 1:
            return all(_eval_leaf(gene_info, {gene_metric_to_flag: gene_metric_value}) for gene_metric_to_flag, gene_metric_value in expression.items())
        return _eval_leaf(gene_info, expression)

    # Unknown structure
    return False


def _status_rank(status: str, status_order: Optional[List[str]]) -> int:
    if not status_order:
        return 0
    try:
        return status_order.index(status)
    except ValueError:
        raise ValueError(
            f"Unknown status '{status}'. " f"Allowed statuses: {status_order}"
        )


def evaluate_gene_rules(
    gene: str, gene_info: Dict[str, Any], rules_yaml: Dict[str, Any]
) -> Tuple[Optional[str], List[RuleMatch]]:
    """
    Evaluate rules for one gene and return (selected_status, matches).

    Expected YAML structure (per gene):
      gene:
        default_status: normal
        status_order: [normal, intermediate, pathological]
        rules:
          - status: intermediate
            when: ...
          - status: pathological
            when: ...

    If `default_status` or `status_order` are omitted, they default to
    "normal" and ["normal", "intermediate", "pathological"] respectively.

    Gene lookup in the rules YAML is case-insensitive (e.g. "f8" and "F8" match).
    """
    gene_rules = rules_yaml.get(gene)
    if not gene_rules and isinstance(rules_yaml, dict):
        gene_lower = gene.lower()
        for k, v in rules_yaml.items():
            if isinstance(k, str) and k.lower() == gene_lower:
                gene_rules = v
                break
    if not gene_rules:
        return None, []

    rules = gene_rules.get("rules") or []
    default_status = gene_rules.get("default_status", "normal")
    status_order = gene_rules.get("status_order") or [
        "normal",
        "intermediate",
        "pathological",
    ]

    matches: List[RuleMatch] = []
    for idx, rule in enumerate(rules):
        status = rule.get("status")
        when = rule.get("when")
        if not status:
            continue
        if eval_when(gene_info, when):
            matches.append(
                RuleMatch(
                    status=status,
                    rule_index=idx,
                    rule=dict(rule),  # copy for JSON output
                )
            )

    if not matches:
        return default_status, []

    # Choose best match based on canonical severity order.
    selected = max(matches, key=lambda m: _status_rank(m.status, status_order))
    return selected.status, matches
