"""Filesystem helpers for project-based storage."""
import json
import shutil
from pathlib import Path
from typing import Any, Optional

class FileStorage:
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def write_json(self, relative_path: str | Path, data: Any) -> Path:
        target = self.base_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return target

    def read_json(self, relative_path: str | Path) -> Any:
        target = self.base_path / relative_path
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)

    def write_text(self, relative_path: str | Path, content: str) -> Path:
        target = self.base_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return target

    def read_text(self, relative_path: str | Path) -> str:
        target = self.base_path / relative_path
        with open(target, "r", encoding="utf-8") as f:
            return f.read()

    def ensure_dir(self, relative_path: str | Path) -> Path:
        target = self.base_path / relative_path
        target.mkdir(parents=True, exist_ok=True)
        return target

    def exists(self, relative_path: str | Path) -> bool:
        return (self.base_path / relative_path).exists()

    def list_files(self, relative_path: str | Path, pattern: str = "*") -> list[Path]:
        target = self.base_path / relative_path
        if not target.exists():
            return []
        return sorted(target.glob(pattern))

    def copy_file(self, src_relative: str | Path, dst_relative: str | Path) -> Path:
        src = self.base_path / src_relative
        dst = self.base_path / dst_relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return dst
