import ast
import operator
import re


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


def calculate(expression):
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("^", "**")

    expression = expression.strip()

    percentage_match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)",
        expression,
        re.IGNORECASE,
    )

    if percentage_match:
        percentage = float(percentage_match.group(1))
        number = float(percentage_match.group(2))

        return (percentage / 100) * number

    tree = ast.parse(expression, mode="eval")

    return evaluate(tree.body)


def evaluate(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Invalid number.")

    if isinstance(node, ast.BinOp):
        operator_function = OPERATORS.get(type(node.op))

        if operator_function is None:
            raise ValueError("Unsupported operator.")

        left = evaluate(node.left)
        right = evaluate(node.right)

        return operator_function(left, right)

    if isinstance(node, ast.UnaryOp):
        value = evaluate(node.operand)

        if isinstance(node.op, ast.USub):
            return -value

        if isinstance(node.op, ast.UAdd):
            return value

    raise ValueError("Invalid mathematical expression.")


def is_calculation_request(message):
    text = message.lower()

    calculation_words = [
        "calculate",
        "what is",
        "how much is",
        "solve",
        "percentage",
    ]

    math_symbols = [
        "+",
        "-",
        "*",
        "/",
        "%",
        "^",
        "×",
        "÷",
    ]

    has_calculation_word = any(
        word in text for word in calculation_words
    )

    has_math_symbol = any(
        symbol in message for symbol in math_symbols
    )

    has_number = any(
        character.isdigit() for character in message
    )

    return has_number and (
        has_calculation_word or has_math_symbol
    )


def extract_expression(message):
    percentage_match = re.search(
        r"(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)",
        message,
        re.IGNORECASE,
    )

    if percentage_match:
        return (
            f"{percentage_match.group(1)}% of "
            f"{percentage_match.group(2)}"
        )

    allowed_characters = "0123456789.+-*/()%^×÷ "

    expression = "".join(
        character
        for character in message
        if character in allowed_characters
    )

    return expression.strip()
