import pytest

from app.tools.calculator import CalculatorInput, calculate, CALCULATOR_TOOL

def test_addition():
    assert calculate(CalculatorInput(expression="2 + 3")) == 5

def test_operator_precedence():
    assert calculate(CalculatorInput(expression="2 + 3 * 4")) == 14

def test_parentheses():
    assert calculate(CalculatorInput(expression="(2 + 3) * 4")) == 20

def test_division():
    assert calculate(CalculatorInput(expression="10 / 4")) == 2.5

def test_power():
    assert calculate(CalculatorInput(expression="2 ** 3")) == 8

def test_negative_numbers():
    assert calculate(CalculatorInput(expression="-5 + 10")) == 5

def test_invalid_syntax_raises_error():
    with pytest.raises(ValueError):
        calculate(CalculatorInput(expression="2 + "))

def test_disallowed_function_call_is_rejected():
    with pytest.raises(ValueError):
        calculate(CalculatorInput(expression="__import__('os').system('echo hi')"))

def test_disallowed_name_is_rejected():
    with pytest.raises(ValueError):
        calculate(CalculatorInput(expression="some_variable + 1"))

def test_tool_metadata_is_correct():
    assert CALCULATOR_TOOL.name == "calculator"
    assert CALCULATOR_TOOL.input_schema is CalculatorInput