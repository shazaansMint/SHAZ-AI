import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

from core.tools.tool_gateway import ToolGateway
from core.coordinator import SHAZCoordinator
from core.router.intent_router import IntentRouter
from core.tools.files.file_tool import FileTool


async def main():
    gateway = ToolGateway()
    calls = []

    async def blocked_tool():
        calls.append("blocked")
        return "This should never run."

    async def confirmation_tool():
        calls.append("confirmed")
        return "Confirmed tool ran."

    gateway.register(
        name="blocked",
        description="A blocked test tool.",
        action="unknown",
        function=blocked_tool,
    )

    gateway.register(
        name="confirmation_required",
        description="A confirmation test tool.",
        action="write",
        function=confirmation_tool,
    )

    try:
        await gateway.execute("blocked")
        raise AssertionError("Blocked tool executed.")
    except PermissionError:
        pass

    assert calls == []

    try:
        await gateway.execute("confirmation_required")
        raise AssertionError("Unconfirmed tool executed.")
    except PermissionError:
        pass

    assert calls == []

    result = await gateway.execute(
        "confirmation_required",
        confirmed=True,
    )

    assert result == "Confirmed tool ran."
    assert calls == ["confirmed"]

    coordinator = SHAZCoordinator.__new__(SHAZCoordinator)
    coordinator.pending_tool = {
        "intent": "test",
        "tool_name": "confirmation_required",
        "kwargs": {},
    }
    coordinator.tool_gateway = gateway
    coordinator.log_activity = lambda message: None

    confirmed = await coordinator.process("confirm")

    assert confirmed["result"]["response"] == "Confirmed tool ran."
    assert calls == ["confirmed", "confirmed"]

    coordinator.pending_tool = {
        "intent": "test",
        "tool_name": "confirmation_required",
        "kwargs": {},
    }

    cancelled = await coordinator.process("cancel")

    assert cancelled["result"]["status"] == "cancelled"
    assert coordinator.pending_tool is None
    assert calls == ["confirmed", "confirmed"]

    with TemporaryDirectory() as temporary_root:
        project_root = Path(temporary_root)
        file_coordinator = SHAZCoordinator.__new__(SHAZCoordinator)
        file_coordinator.router = IntentRouter()
        file_coordinator.pending_tool = None
        file_coordinator.tool_gateway = ToolGateway()
        file_coordinator.log_activity = lambda message: None
        file_coordinator.memory = type(
            "Memory",
            (),
            {"detect_memory": lambda self, message: None},
        )()

        file_coordinator.tool_gateway.register(
            name="file_write",
            description="Write a text file inside the SHAZ project.",
            action="write",
            function=FileTool(project_root).write,
        )

        preview = await file_coordinator.process(
            "write file notes/today.txt :: Buy milk"
        )

        assert preview["result"]["status"] == "confirmation_required"
        assert "Path: notes/today.txt" in preview["result"]["response"]
        assert "Content:\nBuy milk" in preview["result"]["response"]
        assert not (project_root / "notes" / "today.txt").exists()

        written = await file_coordinator.process("confirm")

        assert written["result"]["response"] == (
            "Wrote 8 characters to notes/today.txt."
        )
        assert (
            project_root / "notes" / "today.txt"
        ).read_text(encoding="utf-8") == "Buy milk"

        cancelled_path = project_root / "notes" / "cancelled.txt"
        await file_coordinator.process(
            "write file notes/cancelled.txt :: Do not write"
        )
        cancelled_write = await file_coordinator.process("cancel")

        assert cancelled_write["result"]["status"] == "cancelled"
        assert not cancelled_path.exists()

    print("Tool gateway confirmation lifecycle: OK")


asyncio.run(main())
