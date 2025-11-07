"""Deterministic math evaluator."""

from __future__ import annotations

import ast
import operator as op
from typing import Any, Mapping

from .base import SimpleTool


class MathTool(SimpleTool):
    """Evaluates simple arithmetic expressions."""

    def __init__(self) -> None:
        super().__init__(name="calculator", description="Evaluates basic arithmetic expressions like '2 * (3 + 4)'.")

    def run(self, query: str) -> str:
        expression = query.strip()
        if not expression:
            return "No expression provided."

        try:
            node = ast.parse(expression, mode="eval").body
            value = _safe_eval(node)
            return str(value)
        except Exception as exc:  # pylint: disable=broad-except
            return f"Could not evaluate expression: {exc}"


ALLOWED_OPERATORS: Mapping[type[Any], Any] = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
}


def _safe_eval(node: ast.AST) -> Any:
    if isinstance(node, ast.Num):  # type: ignore[attr-defined]
        return node.n  # type: ignore[attr-defined]
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    raise ValueError("Unsupported expression.")
