from datetime import datetime
from pathlib import Path
import time
import uuid

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

CONFIRMATION_TIMEOUT_SECONDS = 300


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
        self.tool_gateway.register(
            name="file_write",
            description=(
                "Write a text file inside the SHAZ project."
            ),
            action="write",
            function=file_tool.write,
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

        action, request_id = self._parse_confirmation_command(message)

        if action:
            return self._tool_response(
                "tool_confirmation",
                "No pending confirmation request.",
                status="no_pending_request",
            )

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

        if intent == "file_write":
            if message.strip().lower().startswith("write file"):
                request = message.strip()[len("write file"):].strip()
                path, separator, content = request.partition("::")
                path = path.strip()

                if not separator or not path:
                    return self._tool_response(
                        intent,
                        "Use: write file <relative-path> :: <content>",
                    )

                content = content.lstrip()
            else:
                note_request = self.router.note_write_request(message)

                if note_request is None:
                    return self._tool_response(
                        intent,
                        "Use: write file <relative-path> :: <content>",
                    )

                path = "notes/today.txt"
                content = note_request["content"]

            preview = (
                "Write preview:\n"
                f"Path: {path}\n"
                "Content:\n"
                f"{content}"
            )

            return await self._request_tool(
                intent,
                "file_write",
                preview=preview,
                path=path,
                content=content,
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
        preview=None,
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
            request_id = str(uuid.uuid4())
            expires_at = (
                self._now() + CONFIRMATION_TIMEOUT_SECONDS
            )

            self.pending_tool = {
                "intent": intent,
                "tool_name": tool_name,
                "kwargs": kwargs,
                "request_id": request_id,
                "expires_at": expires_at,
            }

            if preview is None:
                preview = "Confirmation required."

            preview = (
                f"{preview}\n\n"
                f"Request ID: {request_id}\n"
                "Reply 'confirm "
                f"{request_id}' to continue or 'cancel "
                f"{request_id}' to stop."
            )

            return self._tool_response(
                intent,
                preview,
                status="confirmation_required",
            )

        return await self._execute_tool(
            intent,
            tool_name,
            confirmed=False,
            **kwargs,
        )

    async def _handle_confirmation(self, message):
        pending_tool = self.pending_tool
        request_id = pending_tool["request_id"]

        if self._now() >= pending_tool["expires_at"]:
            self.pending_tool = None
            self.log_activity(
                f"Confirmation request expired: {request_id}"
            )

            return self._tool_response(
                "tool_confirmation",
                f"Confirmation request {request_id} has expired.",
                status="expired",
            )

        action, supplied_request_id = (
            self._parse_confirmation_command(message)
        )

        if action is None or supplied_request_id is None:
            return self._tool_response(
                "tool_confirmation",
                "Use 'confirm "
                f"{request_id}' or 'cancel {request_id}'.",
                status="confirmation_required",
            )

        if supplied_request_id != request_id:
            return self._tool_response(
                "tool_confirmation",
                "The confirmation request ID does not match the "
                "pending request.",
                status="confirmation_required",
            )

        if action == "confirm":
            self.pending_tool = None

            return await self._execute_tool(
                pending_tool["intent"],
                pending_tool["tool_name"],
                confirmed=True,
                **pending_tool["kwargs"],
            )

        if action == "cancel":
            self.pending_tool = None
            self.log_activity("Pending tool request cancelled.")

            return self._tool_response(
                "tool_confirmation",
                "Cancelled the pending tool request.",
                status="cancelled",
            )

    def _parse_confirmation_command(self, message):
        command = message.strip().split(maxsplit=1)

        if not command:
            return None, None

        action = command[0].lower()

        if action not in {"confirm", "cancel"}:
            return None, None

        if len(command) == 1:
            return action, None

        return action, command[1].strip()

    def _now(self):
        return time.monotonic()

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
