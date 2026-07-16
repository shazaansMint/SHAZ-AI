from pathlib import Path


class FileTool:
    def __init__(self, project_root):
        self.project_root = Path(
            project_root
        ).resolve()

    def _safe_path(self, path):
        requested_path = (
            self.project_root / path
        ).resolve()

        if not requested_path.is_relative_to(
            self.project_root
        ):
            raise PermissionError(
                "File access outside the SHAZ "
                "project is not allowed."
            )

        return requested_path

    async def read(self, path):
        file_path = self._safe_path(path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        if not file_path.is_file():
            raise IsADirectoryError(
                f"Not a file: {path}"
            )

        return file_path.read_text(
            encoding="utf-8"
        )
