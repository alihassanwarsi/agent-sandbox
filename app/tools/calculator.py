import ast
import operator
from pydantic import BaseModel, Field
from app.tools.registry import Tool

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

class CalculatorInput(BaseModel):
    """Input for the calculator tool."""
    expression: str = Field(..., min_length=1, description="A math expression, e.g. '2 + 3 * 4'.")

def _evaluate_node(node: ast.AST) -> float:
    """Recursively evaluate a parsed math expression, allowing only
    numbers and the operators listed in _ALLOWED_OPERATORS."""

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"Operator '{op_type.__name__}' is not allowed.")
        
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)

        return _ALLOWED_OPERATORS[op_type](left, right)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"Operator '{op_type.__name__}' is not allowed.")
        
        operand = _evaluate_node(node.operand)
        return _ALLOWED_OPERATORS[op_type](operand)

    raise ValueError(f"Expression contains a disallowed element: {type(node).__name__}")

def calculate(data: CalculatorInput) -> float:
    """Safely evaluate a math expression and return the result."""
    try:
        parsed = ast.parse(data.expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"'{data.expression}' is not a valid expression.") from exc

    return _evaluate_node(parsed.body)

CALCULATOR_TOOL = Tool(
    name="calculator",
    description="Evaluates a basic math expression (+, -, *, /, **) and returns the result.",
    input_schema=CalculatorInput,
    handler=calculate,
)
