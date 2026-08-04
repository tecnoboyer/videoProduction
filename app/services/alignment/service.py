"""Block 4: Forced Alignment & Word Timestamping.
Uses Whisper (local or API) to derive word-level precision."""
import json
import re
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

    def _safe_read_json(self, file_path: Path) -> Any:
        """Safely read JSON with clear error messages."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        content = file_path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError(f"File is empty: {file_path}")

        # Try parsing as-is first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Clean common issues: single quotes, Python dict literals
        cleaned = content
        # Replace Python single-quoted strings with double-quoted JSON
        # This is a best-effort fix for files like [{'speaker': '...', ...}]
        if "'" in cleaned and '"' not in cleaned:
            cleaned = cleaned.replace("'", '"')
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass

        # If still failing, show preview
        preview = content[:200].replace("\n", " ")
        raise ValueError(
            f"Invalid JSON in {file_path}. Content preview: {preview}"
        )

    def _load_dialogue(self) -> list:
        """Load dialogue array from script output, trying multiple sources."""
        script_dir = self.project_path / "script" / "output"

        # 1. Try output.json FIRST (usually well-formed with {"dialogue": [...]})
        output_json = script_dir / "output.json"
        if output_json.exists():
            try:
                data = self._safe_read_json(output_json)
                if isinstance(data, dict) and "dialogue" in data:
                    dialogue = data["dialogue"]
                    if isinstance(dialogue, list):
                        return dialogue
            except Exception:
                pass  # Fall through to next option

        # 2. Try dialogue.json directly
        dialogue_json = script_dir / "dialogue.json"
        if dialogue_json.exists():
            data = self._safe_read_json(dialogue_json)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "dialogue" in data:
                return data["dialogue"]

        raise FileNotFoundError(
            "No valid dialogue data found. Run script parser first. "
            f"Checked: {output_json}, {dialogue_json}"
        )

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
            # 1. Load master audio
            audio_path = self.project_path / "audio" / "output" / "master_audio.wav"
            if not audio_path.exists():
                raise FileNotFoundError(
                    f"No master_audio.wav found at {audio_path}. Run Audio Assembler first."
                )

            # 2. Load dialogue (robust, tries multiple sources)
            dialogue = self._load_dialogue()
            full_text = " ".join([
                d["text"] for d in dialogue
                if isinstance(d, dict) and "text" in d
            ])
            text_path = self.input_dir / "script_text.txt"
            text_path.write_text(full_text, encoding="utf-8")

            # 3. Run Whisper or fallback
            output_json = self.output_dir / "alignment.json"
            srt_path = self.output_dir / "alignment.srt"

            words = []
            segments = []
            whisper_used = False

            try:
                import whisper
                model_obj = whisper.load_model(model)
                result = model_obj.transcribe(
                    str(audio_path),
                    word_timestamps=True,
                    language=kwargs.get("language", "es"),
                )

                for seg in result.get("segments", []):
                    segments.append(seg)
                    for w in seg.get("words", []):
                        words.append({
                            "word": w["word"].strip(),
                            "start_ms": int(w["start"] * 1000),
                            "end_ms": int(w["end"] * 1000),
                        })

                whisper_used = True

            except ImportError:
                words = self._dummy_alignment(full_text, audio_path)
                segments = [{"start": 0, "end": len(words) * 0.3, "text": full_text}]

            # 4. Save outputs
            output_data = {
                "words": words,
                "segments": segments,
                "whisper_used": whisper_used,
                "model": model if whisper_used else "dummy",
                "total_words": len(words),
            }
            output_json.write_text(
                json.dumps(output_data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            srt_content = self._to_srt(segments) if whisper_used else self._dummy_srt(words)
            srt_path.write_text(srt_content, encoding="utf-8")

            self.job_manager.update_status(
                self.project_id, job_id, "completed",
                result_path=str(output_json)
            )

            return {
                "project_id": self.project_id,
                "words": words,
                "srt_path": str(srt_path),
                "json_path": str(output_json),
                "whisper_used": whisper_used,
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
            lines.append(f"{i}\n{start} --> {end}\n{seg.get('text', '').strip()}\n")
        return "\n".join(lines)

    def _dummy_srt(self, words: list) -> str:
        lines = ["1\n00:00:00,000 --> 00:00:05,000\nWhisper not installed - dummy alignment\n"]
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
