"""Base interface that every service must implement."""
from abc import ABC, abstractmethod
from typing import Any, Dict
from pathlib import Path

class BaseService(ABC):
    service_name: str = "base"

    def __init__(self, project_id: str, project_path: Path):
        self.project_id = project_id
        self.project_path = Path(project_path)
        self.input_dir = self.project_path / self.service_name / "input"
        self.output_dir = self.project_path / self.service_name / "output"
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def generate(self, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    def save(self, filename: str, data: Any) -> Path:
        target = self.output_dir / filename
        if isinstance(data, str):
            target.write_text(data, encoding="utf-8")
        elif isinstance(data, bytes):
            target.write_bytes(data)
        elif isinstance(data, dict):
            import json
            target.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            target.write_text(str(data), encoding="utf-8")
        return target

    def load(self, filename: str) -> Any:
        for src in (self.input_dir, self.output_dir):
            path = src / filename
            if path.exists():
                if path.suffix == ".json":
                    import json
                    return json.loads(path.read_text(encoding="utf-8"))
                return path.read_text(encoding="utf-8")
        raise FileNotFoundError(f"{filename} not found in {self.service_name} input/output")

    def status(self) -> Dict[str, Any]:
        return {
            "service": self.service_name,
            "project_id": self.project_id,
            "input_files": [f.name for f in self.input_dir.iterdir() if f.is_file()],
            "output_files": [f.name for f in self.output_dir.iterdir() if f.is_file()],
        }
