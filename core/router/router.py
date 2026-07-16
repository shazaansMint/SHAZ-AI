from skills.calculator.calculator import (
    calculate,
    extract_expression,
    is_calculation_request,
)


class ShazRouter:
    def route(self, message):
        if is_calculation_request(message):
            return "calculator"

        return "conversation"

    def execute(self, route, message):
        if route == "calculator":
            expression = extract_expression(message)
            result = calculate(expression)

            return f"The answer is {result}."

        return None

