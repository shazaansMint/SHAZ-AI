import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

from core.tools.files.file_tool import FileTool


PROJECT_ROOT = (
    Path(__file__).resolve().parent
)


async def main():
    with TemporaryDirectory() as temporary_root:
        project_root = Path(temporary_root)
        file_tool = FileTool(project_root)

        result = await file_tool.write(
            "notes/today.txt",
            "Buy milk",
        )

        assert result == "Wrote 8 characters to notes/today.txt."
        assert (
            project_root / "notes" / "today.txt"
        ).read_text(encoding="utf-8") == "Buy milk"

        directory = project_root / "notes"

        for path in [
            str(project_root / "absolute.txt"),
            "../outside.txt",
            "notes",
        ]:
            try:
                await file_tool.write(path, "blocked")
                raise AssertionError(f"Unsafe path allowed: {path}")
            except (PermissionError, IsADirectoryError):
                pass

        assert directory.is_dir()

    print("File tool write safety: OK")


asyncio.run(main())
