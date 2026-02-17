from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

NUMERIC_FUNCS = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}

COMPARISON_OPS = {
    ">",
    ">=",
    "<",
    "<=",
    "==",
    "!=",
    "in",
    "not_in",
    "contains",
    "not_contains",
    "not_empty",
}


@dataclass(frozen=True)
class RuleMatch:
    status: str
    rule_index: int
    reason: str

def _get_path_value(obj: Any, path: str) -> Any:
    """
    Get a possibly nested value from dict-like structures.
    Supports dot-paths like 'fusions_called.value.CFH_hap1.type'.
    """
    cur = obj
    for part in path.split("."):
        if cur is None:
            return None
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def _coerce_numeric(x: Any) -> Optional[float]:
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        try:
            return float(x)
        except ValueError:
            return None
    return None


def _apply_op(actual: Any, op: str, expected: Any) -> bool:
    if op not in COMPARISON_OPS:
        raise ValueError(f"Unsupported operator in rules: {op}")

    if op == "not_empty":
        return actual not in (None, "", [], {})

    if op in NUMERIC_OPS:
        a = _coerce_numeric(actual)
        e = _coerce_numeric(expected)
        if a is None or e is None:
            return False
        return NUMERIC_FUNCS[op](a, e)

    if op == "==":
        return actual == expected
    if op == "!=":
        return actual != expected

    if op == "in":
        return actual in (expected or [])
    if op == "not_in":
        return actual not in (expected or [])

    if op == "contains":
        return expected in (actual or [])
    if op == "not_contains":
        return expected not in (actual or [])

    raise ValueError(f"Unsupported operator: {op}")


def _eval_leaf(gene_info: Dict[str, Any], leaf: Dict[str, Any]) -> bool:
    """
    Leaf condition formats supported:
    - { key: scalar } -> equality
    - { key: {">=": 4} } -> operator
    - { key: {"<": 2, ">=": 0} } -> AND across operators
    """
    if len(leaf) != 1:
        # Avoid ambiguous leaf dicts; require single key.
        return False

    key, spec = next(iter(leaf.items()))
    actual = _get_path_value(gene_info, key)

    if isinstance(spec, dict):
        # operator map
        return all(_apply_op(actual, op, expected) for op, expected in spec.items())
    else:
        return _apply_op(actual, "==", spec)


def eval_when(gene_info: Dict[str, Any], expr: Any) -> bool:
    """
    Evaluate a 'when' expression.

    Supported boolean forms:
    - {"all": [expr, expr, ...]}
    - {"any": [expr, expr, ...]}
    - {"not": expr}

    Supported leaf form:
    - {key: value} or {key: {op: value}}

    Backwards-compatible shortcut:
    - {"k1": 1, "k2": {">=": 4}} means AND across keys.
    """
    if expr is None:
        return True

    # Boolean nodes
    if isinstance(expr, dict) and "all" in expr:
        items = expr.get("all") or []
        return all(eval_when(gene_info, item) for item in items)
    if isinstance(expr, dict) and "any" in expr:
        items = expr.get("any") or []
        return any(eval_when(gene_info, item) for item in items)
    if isinstance(expr, dict) and "not" in expr:
        return not eval_when(gene_info, expr.get("not"))

    # Leaf or legacy map-of-leaves
    if isinstance(expr, dict):
        # legacy: multiple keys -> AND of leaves
        if len(expr) > 1:
            return all(_eval_leaf(gene_info, {k: v}) for k, v in expr.items())
        return _eval_leaf(gene_info, expr)

    # Unknown structure
    return False


def _status_rank(status: str, status_order: Optional[List[str]]) -> int:
    if not status_order:
        return 0
    try:
        return status_order.index(status)
    except ValueError:
        raise ValueError(
            f"Unknown status '{status}'. "
            f"Allowed statuses: {status_order}"
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
    """
    gene_rules = rules_yaml.get(gene)
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
                    reason=rule.get("reason") or f"Matched rule {idx} for {gene}",
                )
            )

    if not matches:
        return default_status, []

    # Choose best match based on canonical severity order.
    selected = max(matches, key=lambda m: _status_rank(m.status, status_order))
    return selected.status, matches

