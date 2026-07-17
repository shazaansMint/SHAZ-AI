from datetime import datetime
from pathlib import Path

from skills.calculator.calculator import (
    calculate,
    extract_expression,
)

from core.router.intent_router import IntentRouter
from core.agents.manager import AgentManager
from core.memory import Memory
from core.tools.files.file_tool import FileTool
from core.tools.tool_gateway import ToolGateway


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
        self.tool_gateway = ToolGateway()
        self.pending_tool = None
        self.identity = IDENTITY_FILE.read_text(
            encoding="utf-8"
        )

        file_tool = FileTool(PROJECT_ROOT)
        self.tool_gateway.register(
            name="file_read",
            description=(
                "Read a text file inside the SHAZ project."
            ),
            action="read",
            function=file_tool.read,
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
        if self.pending_tool:
            self.log_activity(
                f"Received confirmation reply: {message}"
            )
            return await self._handle_confirmation(message)

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

        if intent == "file_read":
            path = message.strip()[len("read file"):].strip()

            if not path:
                return self._tool_response(
                    intent,
                    "Please provide a relative file path, for example: "
                    "read file README.md",
                )

            return await self._request_tool(
                intent,
                "file_read",
                path=path,
            )

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

    async def _request_tool(
        self,
        intent,
        tool_name,
        **kwargs,
    ):
        try:
            permission = self.tool_gateway.permission_for(tool_name)
        except ValueError as error:
            return self._tool_response(intent, str(error))

        if permission == "blocked":
            return self._tool_response(
                intent,
                f"Tool blocked: {tool_name}",
            )

        if permission == "confirm":
            self.pending_tool = {
                "intent": intent,
                "tool_name": tool_name,
                "kwargs": kwargs,
            }

            return self._tool_response(
                intent,
                "Confirmation required. Reply 'confirm' to continue "
                "or 'cancel' to stop.",
                status="confirmation_required",
            )

        return await self._execute_tool(
            intent,
            tool_name,
            confirmed=False,
            **kwargs,
        )

    async def _handle_confirmation(self, message):
        reply = message.strip().lower()

        if reply in {"confirm", "yes", "y"}:
            pending_tool = self.pending_tool
            self.pending_tool = None

            return await self._execute_tool(
                pending_tool["intent"],
                pending_tool["tool_name"],
                confirmed=True,
                **pending_tool["kwargs"],
            )

        if reply in {"cancel", "no", "n"}:
            self.pending_tool = None
            self.log_activity("Pending tool request cancelled.")

            return self._tool_response(
                "tool_confirmation",
                "Cancelled the pending tool request.",
                status="cancelled",
            )

        return self._tool_response(
            "tool_confirmation",
            "A tool request is waiting. Reply 'confirm' to continue "
            "or 'cancel' to stop.",
            status="confirmation_required",
        )

    async def _execute_tool(
        self,
        intent,
        tool_name,
        confirmed,
        **kwargs,
    ):
        try:
            result = await self.tool_gateway.execute(
                tool_name,
                confirmed=confirmed,
                **kwargs,
            )
        except (FileNotFoundError, IsADirectoryError, PermissionError, ValueError) as error:
            self.log_activity(
                f"Tool execution failed: {tool_name}. Error: {error}"
            )
            return self._tool_response(intent, str(error))

        self.log_activity(f"Tool result: {tool_name}")

        return self._tool_response(intent, result)

    def _tool_response(self, intent, response, status="completed"):
        return {
            "intent": intent,
            "result": {
                "source": "tool",
                "status": status,
                "response": response,
            },
        }
