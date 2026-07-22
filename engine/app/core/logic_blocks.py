"""Logic block evaluator for condition and loop blocks."""

import re
from typing import Any

from .template_parser import (
    IF_BLOCK_START, IF_BLOCK_ELSE, IF_BLOCK_END,
    EACH_BLOCK_START, EACH_BLOCK_END,
)


def evaluate_condition(expression: str, variables: dict[str, Any]) -> bool:
    """Evaluate a condition expression against variable values.

    Supports:
    - `variable` (truthy check)
    - `variable == "value"` (string equality)
    - `variable != "value"` (string inequality)
    - `variable > N`, `variable < N` (numeric comparison)
    """
    expr = expression.strip()

    # Simple truthy check: just a variable name
    if " " not in expr and "==" not in expr and "!=" not in expr:
        value = _resolve_variable(expr, variables)
        return bool(value)

    # Comparison operators
    for op in ["!=", "==", ">=", "<=", ">", "<"]:
        if op in expr:
            parts = expr.split(op, 1)
            var_name = parts[0].strip()
            target = parts[1].strip().strip("\"'")
            value = _resolve_variable(var_name, variables)

            try:
                if op == "==":
                    return str(value) == str(target)
                elif op == "!=":
                    return str(value) != str(target)
                elif op in (">=", "<=", ">", "<"):
                    return _numeric_compare(value, target, op)
            except (ValueError, TypeError):
                return False

    return False


def _resolve_variable(name: str, variables: dict) -> Any:
    """Resolve a variable name, supporting dot notation for nested objects."""
    parts = name.split(".")
    value = variables
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part)
        elif isinstance(value, list) and part.isdigit():
            value = value[int(part)]
        else:
            return None
    return value


def _numeric_compare(value: Any, target: str, op: str) -> bool:
    """Compare a value against a numeric target."""
    val = float(value)
    tgt = float(target)
    if op == ">":
        return val > tgt
    elif op == "<":
        return val < tgt
    elif op == ">=":
        return val >= tgt
    elif op == "<=":
        return val <= tgt
    return False
