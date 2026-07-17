import re

from skills.calculator.calculator import is_calculation_request


class IntentRouter:
    def route(self, message):
        text = message.lower()

        if text == "write file" or text.startswith("write file "):
            return "file_write"

        if text == "read file" or text.startswith("read file "):
            return "file_read"

        if self.note_write_request(message):
            return "file_write"

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

    def note_write_request(self, message):
        match = re.fullmatch(
            r"\s*(?:i\s+(?:want|would\s+like|need)\s+"
            r"(?:you\s+)?to\s+)?(?:please\s+)?"
            r"(?:create|write|make)\s+(?:a\s+)?note\s+"
            r"(?:saying(?:\s+that)?|that\s+says|"
            r"with\s+(?:the\s+)?content)\s+"
            r"(?P<content>.+?)\s*",
            message,
            re.IGNORECASE,
        )

        if match is None:
            return None

        content = match.group("content").strip()

        if not content:
            return None

        return {"content": content[0].upper() + content[1:]}
