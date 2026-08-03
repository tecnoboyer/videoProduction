"""Narrative Service: transforms raw text into structured narrative,
injecting RAG from the project's master document."""
import json
import re
from pathlib import Path
from typing import Any, Optional
from app.services.base_service import BaseService
from app.services.providers.factory import ProviderFactory
from app.services.job.manager import JobManager
from app.core.config import get_settings

class NarrativeService(BaseService):
    service_name = "narrative"

    def __init__(self, project_id: str, project_path: Path):
        super().__init__(project_id, project_path)
        self.job_manager = JobManager()
        self.llm = None

    async def _get_llm(self, provider: Optional[str] = None):
        if self.llm is None:
            self.llm = ProviderFactory.get_llm(provider)
        return self.llm

    def _load_master_doc(self) -> str:
        master_path = self.project_path / "rag" / "input" / "master_doc.md"
        if master_path.exists():
            return master_path.read_text(encoding="utf-8")
        return ""

    def validate(self, data: Any) -> bool:
        return isinstance(data, str) and len(data.strip()) > 10

    async def generate(
        self,
        raw_text: str,
        style_hints: str = "",
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
            self.save("raw_input.txt", raw_text)
            master_doc = self._load_master_doc()

            system_prompt = f"""You are an expert narrative designer for video production.
You transform raw storytelling text into polished, structured narratives.

## PROJECT PRINCIPLES (from Master Document)
{master_doc[:4000]}

## INSTRUCTIONS
- Maintain the natural, human-friendly storytelling tone.
- Identify characters, scenes, and emotional arcs.
- Output a clean narrative text plus a structured summary.
- Respect all principles and objeciones de conciencia from the Master Document.
- Language: same as input.
"""

            user_prompt = f"""RAW NARRATIVE:
{raw_text}

STYLE HINTS: {style_hints}

Please output ONLY a JSON object with this structure:
{{
  "narrative_text": "the polished full narrative",
  "summary": "one-paragraph summary",
  "characters": ["Character1", "Character2"],
  "scenes_count": 3,
  "notes": "any production notes"
}}
"""

            llm = await self._get_llm(provider)
            response = await llm.generate(user_prompt, system_prompt=system_prompt)

            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {
                    "narrative_text": response,
                    "summary": "",
                    "characters": [],
                    "scenes_count": None,
                    "notes": "Raw response (JSON parsing failed)"
                }

            self.save("output.json", result)
            self.save("narrative.txt", result.get("narrative_text", ""))

            self.job_manager.update_status(
                self.project_id, job_id, "completed",
                result_path=str(self.output_dir / "output.json")
            )

            return {
                **result,
                "project_id": self.project_id,
                "output_path": str(self.output_dir / "output.json"),
                "job_id": job_id,
            }

        except Exception as e:
            self.job_manager.update_status(
                self.project_id, job_id, "failed",
                error_message=str(e)
            )
            raise
