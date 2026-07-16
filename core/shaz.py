from datetime import datetime
from pathlib import Path

from core.brain.ollama_client import OllamaBrain
from core.router.router import ShazRouter
from core.memory import Memory


PROJECT_ROOT = Path(__file__).resolve().parents[1]


IDENTITY_FILE = (
    PROJECT_ROOT
    / "core"
    / "identity"
    / "shaz_identity.md"
)


JOURNAL_FILE = (
    PROJECT_ROOT
    / "journal"
    / "activity.log"
)


class SHAZ:
    def __init__(self):
        self.identity = self.load_identity()
        self.brain = OllamaBrain()
        self.router = ShazRouter()
        self.memory = Memory()

    def load_identity(self):
        return IDENTITY_FILE.read_text(
            encoding="utf-8"
        )

    def log_activity(self, message):
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        JOURNAL_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with JOURNAL_FILE.open(
            "a",
            encoding="utf-8",
        ) as journal:
            journal.write(
                f"[{timestamp}] {message}\n"
            )

    def talk(self, message):
        route = self.router.route(message)

        self.log_activity(
            f"Received request. Route: {route}. "
            f"Message: {message}"
        )

        detected_memory = (
            self.memory.detect_memory(message)
        )

        if detected_memory:
            saved = self.memory.save(
                detected_memory
            )

            if saved:
                self.log_activity(
                    "New memory saved: "
                    f"{detected_memory}"
                )

                return (
                    "Got it. I'll remember that."
                )

            return (
                "I already have that in my memory."
            )

        skill_result = self.router.execute(
            route,
            message,
        )

        if skill_result:
            self.log_activity(
                f"Skill result: {skill_result}"
            )

            return skill_result

        memory_context = self.memory.read()

        response = self.brain.chat(
            messages=[
                {
                    "role": "system",
                    "content": self.identity,
                },
                {
                    "role": "system",
                    "content": (
                        "Known SHAZ memory:\n"
                        f"{memory_context}"
                    ),
                },
                {
                    "role": "user",
                    "content": message,
                },
            ]
        )

        self.log_activity(
            "SHAZ generated a conversation response."
        )

        return response


def main():
    shaz = SHAZ()

    print()
    print("=================================")
    print("        SHAZ IS ONLINE")
    print("=================================")
    print()
    print("Qwen3 8B connected.")
    print("Type 'exit' to shut down SHAZ.")
    print()

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print()
                print("SHAZ: Shutting down.")
                break

            response = shaz.talk(user_input)

            print()
            print(f"SHAZ: {response}")
            print()

        except KeyboardInterrupt:
            print()
            print("SHAZ: Shutting down.")
            break

        except Exception as error:
            print()
            print(f"SHAZ Error: {error}")
            print()


if __name__ == "__main__":
    main()
