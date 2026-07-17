import asyncio

from core.tools.tool_gateway import ToolGateway
from core.coordinator import SHAZCoordinator


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

    print("Tool gateway confirmation lifecycle: OK")


asyncio.run(main())
