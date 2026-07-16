import asyncio
from pathlib import Path

from core.tools.files.file_tool import FileTool
from core.tools.tool_gateway import ToolGateway


PROJECT_ROOT = (
    Path(__file__).resolve().parent
)


async def main():
    gateway = ToolGateway()

    file_tool = FileTool(
        PROJECT_ROOT
    )

    gateway.register(
        name="file_read",
        description=(
            "Read a text file inside the "
            "SHAZ project."
        ),
        action="read",
        function=file_tool.read,
    )

    print(
        gateway.describe_tools()
    )

    content = await gateway.execute(
        "file_read",
        path="core/identity/shaz_identity.md",
    )

    print()
    print(content[:500])


asyncio.run(main())
