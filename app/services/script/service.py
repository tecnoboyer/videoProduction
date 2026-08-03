"""Block 1: Script & Dialogue Parser.
Transforms narrative (or raw text) into structured dialogue events."""
import json
import re
from pathlib import Path
from typing import Any, Optional, List
from app.services.base_service import BaseService
from app.services.providers.factory import ProviderFactory
from app.services.job.manager import JobManager
from app.schemas.script import DialogueEvent
from app.core.config import get_settings

class ScriptService(BaseService):
    service_name = "script"

    def __init__(self, project_id: str, project_path: Path):
        super().__init__(project_id, project_path)
        self.job_manager = JobManager()

    def validate(self, data: Any) -> bool:
        if isinstance(data, list):
            return all("speaker" in d and "text" in d for d in data)
        return isinstance(data, str) and len(data.strip()) > 0

    async def generate(
        self,
        source: str = "narrative",
        raw_text: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs: Any
    ) -> dict:
        job_id = self.job_manager.create_job(
            project_id=self.project_id,
            service_name=self.service_name,
            provider=provider or get_settings().DEFAULT_LLM_PROVIDER,
            input_folder=str(self.input_dir),
            output_folder=str(self.output_dir),
        )
        self.job_manager.update_status(self.project_id, job_id, "running")

        try:
            if source == "narrative":
                narrative_path = self.project_path / "narrative" / "output" / "narrative.txt"
                if narrative_path.exists():
                    text = narrative_path.read_text(encoding="utf-8")
                else:
                    raise FileNotFoundError("No narrative output found. Run narrative first.")
            elif source == "raw":
                text = raw_text or ""
            elif source == "file":
                file_path = kwargs.get("file_path")
                text = Path(file_path).read_text(encoding="utf-8") if file_path else ""
            else:
                raise ValueError(f"Unknown source: {source}")

            self.save("input_text.txt", text)

            master_path = self.project_path / "rag" / "input" / "master_doc.md"
            master_doc = master_path.read_text(encoding="utf-8") if master_path.exists() else ""

            system_prompt = f"""You are a script parser for video production.
Convert narrative text into structured dialogue events.

## MASTER DOCUMENT PRINCIPLES
{master_doc[:3000]}

## RULES
- Each line of dialogue must have: speaker, text, voice_id (guess based on speaker name), emotion, direction.
- Group dialogue into scenes if natural breaks exist.
- Respect the principles above: no harmful content, accurate, inclusive.
- Output ONLY valid JSON array.
"""
            user_prompt = f"""Convert this narrative into a JSON array of dialogue events:

{text}

Expected format:
[
  {{"speaker": "Alice", "text": "Did you see that?", "voice_id": "v_alice_01", "emotion": "surprised", "direction": "looking up", "scene_id": "scene_001"}},
  ...
]
"""

            llm = ProviderFactory.get_llm(provider)
            response = await llm.generate(user_prompt, system_prompt=system_prompt)

            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON array found in LLM response")
            dialogue = json.loads(json_match.group())

            scenes = {}
            for d in dialogue:
                sid = d.get("scene_id", "scene_001")
                scenes.setdefault(sid, []).append(d)
            scene_breakdown = [{"scene_id": k, "lines": len(v)} for k, v in scenes.items()]

            output = {
                "dialogue": dialogue,
                "scene_breakdown": scene_breakdown,
                "clip_count": len(dialogue),
            }
            self.save("output.json", output)
            self.save("dialogue.json", dialogue)

            self.job_manager.update_status(
                self.project_id, job_id, "completed",
                result_path=str(self.output_dir / "output.json")
            )

            return {
                **output,
                "project_id": self.project_id,
                "output_path": str(self.output_dir / "output.json"),
                "job_id": job_id,
            }

        except Exception as e:
            self.job_manager.update_status(self.project_id, job_id, "failed", error_message=str(e))
            raise
