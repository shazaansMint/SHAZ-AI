import asyncio
from pathlib import Path

from core.tools.files.file_tool import FileTool


PROJECT_ROOT = (
    Path(__file__).resolve().parent
)


async def main():
    file_tool = FileTool(
        PROJECT_ROOT
    )

    content = await file_tool.read(
        "README.md"
    )

    print(content[:500])


asyncio.run(main())
