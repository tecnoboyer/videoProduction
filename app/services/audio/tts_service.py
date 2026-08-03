"""Block 2: Audio Synthesis (TTS Engine).
Generates individual audio clips for each dialogue line."""
import json
import re
from pathlib import Path
from typing import Any, Optional, List
from app.services.base_service import BaseService
from app.services.providers.factory import ProviderFactory
from app.services.job.manager import JobManager
from app.core.config import get_settings


class TTSService(BaseService):
    service_name = "audio"

    def __init__(self, project_id: str, project_path: Path):
        super().__init__(project_id, project_path)
        self.job_manager = JobManager()
        self.clips_dir = self.output_dir / "clips"
        self.clips_dir.mkdir(parents=True, exist_ok=True)

    def validate(self, data: Any) -> bool:
        if isinstance(data, list):
            return all("text" in d and "voice_id" in d for d in data)
        return False

    def _load_and_clean_json(self, file_path: Path) -> list:
        """Lee y sanitiza un archivo JSON manejando comillas envolventes o bloques markdown."""
        content = file_path.read_text(encoding="utf-8").strip()

        # 1. Eliminar comillas envolventes si las hay (ej. `' { ... } '`)
        if (content.startswith("'") and content.endswith("'")) or (content.startswith('"') and content.endswith('"')):
            content = content[1:-1].strip()

        # 2. Eliminar bloques de código markdown ```json ... ```
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
            content = re.sub(r"\s*```$", "", content)
            content = content.strip()

        data = json.loads(content)

        # 3. Extraer la lista 'dialogue' si el JSON viene en formato objeto {"dialogue": [...]}
        if isinstance(data, dict) and "dialogue" in data:
            return data["dialogue"]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError(f"Estructura JSON no reconocida en {file_path}. Se esperaba una lista o un objeto con clave 'dialogue'.")

    async def generate(
        self,
        provider: Optional[str] = None,
        voice_settings: Optional[dict] = None,
        clips: Optional[List[dict]] = None,
        **kwargs: Any
    ) -> dict:
        job_id = self.job_manager.create_job(
            project_id=self.project_id,
            service_name="audio_tts",
            provider=provider or get_settings().DEFAULT_TTS_PROVIDER,
            input_folder=str(self.input_dir),
            output_folder=str(self.output_dir),
        )
        self.job_manager.update_status(self.project_id, job_id, "running")

        try:
            if clips is None:
                script_dir = self.project_path / "script" / "output"
                output_json_path = script_dir / "output.json"
                dialogue_json_path = script_dir / "dialogue.json"

                # Comprobamos output.json primero, y luego dialogue.json
                if output_json_path.exists():
                    clips = self._load_and_clean_json(output_json_path)
                elif dialogue_json_path.exists():
                    clips = self._load_and_clean_json(dialogue_json_path)
                else:
                    raise FileNotFoundError("No output.json or dialogue.json found. Run script parser first.")

            self.save("input_clips.json", clips)
            tts = ProviderFactory.get_tts(provider)

            generated = []
            for i, clip in enumerate(clips):
                clip_id = clip.get("scene_id", "scene") + f"_clip_{i:03d}"
                output_file = self.clips_dir / f"{clip_id}.mp3"
                await tts.generate_voice(
                    text=clip["text"],
                    voice_id=clip.get("voice_id", "Rachel"),
                    output_path=str(output_file),
                    **(voice_settings or {})
                )
                generated.append({
                    "clip_id": clip_id,
                    "speaker": clip.get("speaker", "unknown"),
                    "text": clip["text"],
                    "voice_id": clip.get("voice_id", ""),
                    "output_file": str(output_file),
                })

            manifest = {"clips": generated, "total_clips": len(generated)}
            self.save("tts_manifest.json", manifest)

            self.job_manager.update_status(
                self.project_id, job_id, "completed",
                result_path=str(self.output_dir / "tts_manifest.json")
            )

            return {
                **manifest,
                "project_id": self.project_id,
                "clips_dir": str(self.clips_dir),
                "job_id": job_id,
            }

        except Exception as e:
            self.job_manager.update_status(self.project_id, job_id, "failed", error_message=str(e))
            raise