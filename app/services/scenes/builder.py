"""Block 5: Visual Asset & Scene Builder.
Generates scene composition manifest from alignment + images."""
import json
from pathlib import Path
from typing import Any, Optional, List
from app.services.base_service import BaseService
from app.services.job.manager import JobManager


class SceneBuilder(BaseService):
    service_name = "scenes"

    def __init__(self, project_id: str, project_path: Path):
        super().__init__(project_id, project_path)
        self.job_manager = JobManager()

    def _safe_read_json(self, file_path: Path) -> Any:
        """Safely read JSON with fallback for single-quoted files."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        content = file_path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError(f"File is empty: {file_path}")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        # Fix single quotes
        if "'" in content and '"' not in content:
            cleaned = content.replace("'", '"')
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass
        preview = content[:200].replace("\n", " ")
        raise ValueError(f"Invalid JSON in {file_path}. Preview: {preview}")

    def _load_dialogue(self) -> list:
        """Load dialogue array, trying multiple sources."""
        script_dir = self.project_path / "script" / "output"
        # 1. Try output.json first
        output_json = script_dir / "output.json"
        if output_json.exists():
            try:
                data = self._safe_read_json(output_json)
                if isinstance(data, dict) and "dialogue" in data:
                    return data["dialogue"]
            except Exception:
                pass
        # 2. Try dialogue.json
        dialogue_json = script_dir / "dialogue.json"
        if dialogue_json.exists():
            data = self._safe_read_json(dialogue_json)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "dialogue" in data:
                return data["dialogue"]
        return []

    def validate(self, data: Any) -> bool:
        return isinstance(data, dict)

    async def generate(
        self,
        composition_style: str = "default",
        **kwargs: Any
    ) -> dict:
        job_id = self.job_manager.create_job(
            project_id=self.project_id,
            service_name=self.service_name,
            provider="internal",
            input_folder=str(self.input_dir),
            output_folder=str(self.output_dir),
        )
        self.job_manager.update_status(self.project_id, job_id, "running")

        try:
            # 1. Load alignment
            align_path = self.project_path / "alignment" / "output" / "alignment.json"
            if not align_path.exists():
                raise FileNotFoundError("No alignment found. Run Alignment first.")
            alignment = self._safe_read_json(align_path)
            words = alignment.get("words", []) if isinstance(alignment, dict) else []

            # 2. Load dialogue (robust)
            dialogue = self._load_dialogue()

            # 3. Load available images
            images_dir = self.project_path / "images" / "output"
            images = sorted([
                str(f) for f in images_dir.glob("*")
                if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
            ])

            # 4. Build scene compositions
            scenes = []
            scene_duration_ms = 5000

            for i, dlg in enumerate(dialogue):
                if not isinstance(dlg, dict):
                    continue
                scene_id = dlg.get("scene_id", f"scene_{i:03d}")
                start_ms = i * scene_duration_ms
                end_ms = start_ms + scene_duration_ms
                bg = images[i % len(images)] if images else None

                scenes.append({
                    "scene_id": scene_id,
                    "start_ms": start_ms,
                    "end_ms": end_ms,
                    "active_speaker": dlg.get("speaker"),
                    "background_image": bg,
                    "subtitle_text": dlg.get("text", ""),
                    "subtitle_style": {
                        "font": "Arial",
                        "size": 48,
                        "color": "white",
                        "outline": "black",
                        "position": "bottom",
                    },
                    "effects": ["fade_in"] if i == 0 else [],
                })

            # 5. Save manifest
            manifest = {
                "scenes": scenes,
                "composition_style": composition_style,
                "total_scenes": len(scenes),
            }
            manifest_path = self.output_dir / "scene_manifest.json"
            manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            self.job_manager.update_status(
                self.project_id, job_id, "completed",
                result_path=str(manifest_path)
            )

            return {
                **manifest,
                "project_id": self.project_id,
                "manifest_path": str(manifest_path),
                "job_id": job_id,
            }

        except Exception as e:
            self.job_manager.update_status(self.project_id, job_id, "failed", error_message=str(e))
            raise
