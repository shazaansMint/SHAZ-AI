import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

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
    current_time = 100.0
    coordinator.pending_tool = None
    coordinator.tool_gateway = gateway
    coordinator.log_activity = lambda message: None
    coordinator._now = lambda: current_time

    pending = await coordinator._request_tool(
        "test",
        "confirmation_required",
    )
    request_id = coordinator.pending_tool["request_id"]

    UUID(request_id)
    assert request_id in pending["result"]["response"]
    assert coordinator.pending_tool["expires_at"] == 400.0

    missing_id = await coordinator.process("confirm")

    assert missing_id["result"]["status"] == "confirmation_required"
    assert coordinator.pending_tool["request_id"] == request_id
    assert calls == ["confirmed"]

    incorrect = await coordinator.process("confirm incorrect-id")

    assert incorrect["result"]["status"] == "confirmation_required"
    assert coordinator.pending_tool["request_id"] == request_id
    assert calls == ["confirmed"]

    confirmed = await coordinator.process(f"confirm {request_id}")

    assert confirmed["result"]["response"] == "Confirmed tool ran."
    assert calls == ["confirmed", "confirmed"]
    assert coordinator.pending_tool is None

    duplicate = await coordinator.process(f"confirm {request_id}")

    assert duplicate["result"]["status"] == "no_pending_request"
    assert calls == ["confirmed", "confirmed"]

    await coordinator._request_tool("test", "confirmation_required")
    cancellation_id = coordinator.pending_tool["request_id"]
    assert cancellation_id != request_id

    cancelled = await coordinator.process(f"cancel {cancellation_id}")

    assert cancelled["result"]["status"] == "cancelled"
    assert coordinator.pending_tool is None
    assert calls == ["confirmed", "confirmed"]

    await coordinator._request_tool("test", "confirmation_required")
    expired_id = coordinator.pending_tool["request_id"]
    assert expired_id not in {request_id, cancellation_id}
    current_time = 401.0

    expired = await coordinator.process(f"confirm {expired_id}")

    assert expired["result"]["status"] == "expired"
    assert coordinator.pending_tool is None
    assert calls == ["confirmed", "confirmed"]

    with TemporaryDirectory() as temporary_root:
        project_root = Path(temporary_root)
        file_coordinator = SHAZCoordinator.__new__(SHAZCoordinator)
        file_coordinator.router = IntentRouter()
        file_coordinator.pending_tool = None
        file_coordinator.tool_gateway = ToolGateway()
        file_coordinator.log_activity = lambda message: None
        file_coordinator._now = lambda: 100.0
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
        write_request_id = file_coordinator.pending_tool["request_id"]
        assert write_request_id in preview["result"]["response"]
        assert not (project_root / "notes" / "today.txt").exists()

        written = await file_coordinator.process(
            f"confirm {write_request_id}"
        )

        assert written["result"]["response"] == (
            "Wrote 8 characters to notes/today.txt."
        )
        assert (
            project_root / "notes" / "today.txt"
        ).read_text(encoding="utf-8") == "Buy milk"

        cancelled_path = project_root / "notes" / "cancelled.txt"
        cancelled_preview = await file_coordinator.process(
            "write file notes/cancelled.txt :: Do not write"
        )
        cancelled_request_id = file_coordinator.pending_tool["request_id"]
        assert cancelled_request_id in cancelled_preview["result"]["response"]
        cancelled_write = await file_coordinator.process(
            f"cancel {cancelled_request_id}"
        )

        assert cancelled_write["result"]["status"] == "cancelled"
        assert not cancelled_path.exists()

    print("Tool gateway confirmation lifecycle: OK")


asyncio.run(main())
