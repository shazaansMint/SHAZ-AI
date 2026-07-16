from datetime import datetime
from pathlib import Path

from skills.calculator.calculator import (
    calculate,
    extract_expression,
)

from core.router.intent_router import IntentRouter
from core.agents.manager import AgentManager
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


class SHAZCoordinator:
    def __init__(self):
        self.router = IntentRouter()
        self.agent_manager = AgentManager()
        self.memory = Memory()
        self.identity = IDENTITY_FILE.read_text(
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
            journal.write(f"[{timestamp}] {message}\n")

    async def process(self, message):
        intent = self.router.route(message)

        self.log_activity(
            f"Received request. Route: {intent}. "
            f"Message: {message}"
        )

        detected_memory = self.memory.detect_memory(message)

        if detected_memory:
            saved = self.memory.save(detected_memory)

            if saved:
                response = "Got it. I'll remember that."
                self.log_activity(
                    f"New memory saved: {detected_memory}"
                )
            else:
                response = "I already have that in my memory."

            return {
                "intent": "memory",
                "result": {
                    "source": "memory",
                    "response": response,
                },
            }

        if intent == "calculator":
            expression = extract_expression(message)
            response = f"The answer is {calculate(expression)}."
            self.log_activity(f"Skill result: {response}")

            return {
                "intent": intent,
                "result": {
                    "source": "calculator",
                    "response": response,
                },
            }

        context = {
            "identity": self.identity,
            "memory": self.memory.read(),
        }

        result = await self.agent_manager.run(
            intent,
            message,
            context,
        )

        self.log_activity(
            f"SHAZ generated a {result['agent']} response."
        )

        return {
            "intent": intent,
            "result": result,
        }
