"""Block 4: Forced Alignment & Word Timestamping.
Uses Whisper (local or API) to derive word-level precision."""
import json
import subprocess
from pathlib import Path
from typing import Any, Optional
from app.services.base_service import BaseService
from app.services.job.manager import JobManager

class AlignmentService(BaseService):
    service_name = "alignment"

    def __init__(self, project_id: str, project_path: Path):
        super().__init__(project_id, project_path)
        self.job_manager = JobManager()

    def validate(self, data: Any) -> bool:
        return isinstance(data, dict) and "master_audio_path" in data

    async def generate(
        self,
        provider: str = "whisper",
        model: str = "base",
        **kwargs: Any
    ) -> dict:
        job_id = self.job_manager.create_job(
            project_id=self.project_id,
            service_name=self.service_name,
            provider=provider,
            input_folder=str(self.input_dir),
            output_folder=str(self.output_dir),
        )
        self.job_manager.update_status(self.project_id, job_id, "running")

        try:
            audio_path = self.project_path / "audio" / "output" / "master_audio.wav"
            script_path = self.project_path / "script" / "output" / "dialogue.json"

            if not audio_path.exists():
                raise FileNotFoundError("No master_audio.wav found. Run Audio Assembler first.")
            if not script_path.exists():
                raise FileNotFoundError("No dialogue.json found. Run Script Parser first.")

            dialogue = json.loads(script_path.read_text(encoding="utf-8"))
            full_text = " ".join([d["text"] for d in dialogue])
            text_path = self.input_dir / "script_text.txt"
            text_path.write_text(full_text, encoding="utf-8")

            output_json = self.output_dir / "alignment.json"

            try:
                import whisper
                model_obj = whisper.load_model(model)
                result = model_obj.transcribe(str(audio_path), word_timestamps=True, language=kwargs.get("language", "es"))

                words = []
                for seg in result.get("segments", []):
                    for w in seg.get("words", []):
                        words.append({
                            "word": w["word"].strip(),
                            "start_ms": int(w["start"] * 1000),
                            "end_ms": int(w["end"] * 1000),
                        })

                with open(output_json, "w", encoding="utf-8") as f:
                    json.dump({"words": words, "segments": result.get("segments", [])}, f, indent=2, ensure_ascii=False)

                srt_path = self.output_dir / "alignment.srt"
                srt_path.write_text(self._to_srt(result.get("segments", [])), encoding="utf-8")

            except ImportError:
                words = self._dummy_alignment(full_text, audio_path)
                with open(output_json, "w", encoding="utf-8") as f:
                    json.dump({"words": words, "note": "whisper not installed - dummy data"}, f, indent=2)
                srt_path = self.output_dir / "alignment.srt"
                srt_path.write_text("1\n00:00:00,000 --> 00:00:05,000\nWhisper not installed\n", encoding="utf-8")

            self.job_manager.update_status(
                self.project_id, job_id, "completed",
                result_path=str(output_json)
            )

            return {
                "project_id": self.project_id,
                "words": words,
                "srt_path": str(srt_path),
                "json_path": str(output_json),
                "job_id": job_id,
            }

        except Exception as e:
            self.job_manager.update_status(self.project_id, job_id, "failed", error_message=str(e))
            raise

    def _to_srt(self, segments: list) -> str:
        lines = []
        for i, seg in enumerate(segments, 1):
            start = self._fmt_time(seg["start"])
            end = self._fmt_time(seg["end"])
            lines.append(f"{i}\n{start} --> {end}\n{seg['text'].strip()}\n")
        return "\n".join(lines)

    def _fmt_time(self, seconds: float) -> str:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    def _dummy_alignment(self, text: str, audio_path: Path) -> list:
        words = text.split()
        result = []
        t = 0
        for w in words:
            duration = max(200, len(w) * 150)
            result.append({"word": w, "start_ms": t, "end_ms": t + duration})
            t += duration + 80
        return result
