from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


LONG_TERM_MEMORY = (
    PROJECT_ROOT
    / "memory"
    / "long_term"
    / "facts.md"
)


class Memory:
    def __init__(self):
        LONG_TERM_MEMORY.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        LONG_TERM_MEMORY.touch(
            exist_ok=True
        )

    def save(self, memory):
        memory = memory.strip()

        if not memory:
            return False

        existing_memories = self.read().splitlines()

        formatted_memory = f"- {memory}"

        if formatted_memory in existing_memories:
            return False

        with LONG_TERM_MEMORY.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(
                f"{formatted_memory}\n"
            )

        return True

    def read(self):
        return LONG_TERM_MEMORY.read_text(
            encoding="utf-8"
        )

    def search(self, keyword):
        memories = self.read().splitlines()

        keyword = keyword.lower()

        return [
            memory
            for memory in memories
            if keyword in memory.lower()
        ]

    def detect_memory(self, message):
        text = message.strip()

        lower_text = text.lower()

        memory_triggers = [
            "remember that ",
            "remember ",
            "don't forget that ",
            "dont forget that ",
            "don't forget ",
            "dont forget ",
        ]

        for trigger in memory_triggers:
            if lower_text.startswith(trigger):
                memory = text[len(trigger):].strip()

                return memory

        return None
