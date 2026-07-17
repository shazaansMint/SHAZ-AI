from skills.calculator.calculator import is_calculation_request


class IntentRouter:
    def route(self, message):
        text = message.lower()

        if text == "write file" or text.startswith("write file "):
            return "file_write"

        if text == "read file" or text.startswith("read file "):
            return "file_read"

        if is_calculation_request(message):
            return "calculator"

        if any(
            word in text
            for word in [
                "code",
                "coding",
                "python",
                "program",
                "debug",
                "bug",
            ]
        ):
            return "coding"

        return "conversation"
