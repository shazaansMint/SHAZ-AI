import asyncio

from core.tools.tool_gateway import ToolGateway


async def dangerous_tool():
    return "This should never run."


async def main():
    gateway = ToolGateway()

    gateway.register(
        "dangerous",
        dangerous_tool,
        action="unknown",
    )

    try:
        result = await gateway.execute(
            "dangerous"
        )

        print(result)

    except PermissionError as error:
        print(
            f"PERMISSION BLOCKED: {error}"
        )


asyncio.run(main())
