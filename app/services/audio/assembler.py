"""Block 3: Audio Assembler & Timeline Composer.
Stitches clips into a continuous master audio track."""
import json
import subprocess
from pathlib import Path
from typing import Any, Optional, List
from app.services.base_service import BaseService
from app.services.job.manager import JobManager

class AudioAssembler(BaseService):
    service_name = "audio"

    def __init__(self, project_id: str, project_path: Path):
        super().__init__(project_id, project_path)
        self.job_manager = JobManager()

    def validate(self, data: Any) -> bool:
        return isinstance(data, list) and len(data) > 0

    async def generate(
        self,
        padding_ms: int = 300,
        normalize: bool = True,
        **kwargs: Any
    ) -> dict:
        job_id = self.job_manager.create_job(
            project_id=self.project_id,
            service_name="audio_assembler",
            provider="ffmpeg",
            input_folder=str(self.input_dir),
            output_folder=str(self.output_dir),
        )
        self.job_manager.update_status(self.project_id, job_id, "running")

        try:
            manifest_path = self.project_path / "audio" / "output" / "tts_manifest.json"
            if not manifest_path.exists():
                raise FileNotFoundError("No TTS manifest found. Run TTS first.")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            clips = manifest["clips"]

            inputs = []
            for i, clip in enumerate(clips):
                inputs.extend(["-i", clip["output_file"]])

            master_path = self.output_dir / "master_audio.wav"
            filter_str = "concat=n=" + str(len(clips)) + ":v=0:a=1"
            cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_str, "-ar", "44100", "-ac", "2", str(master_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg error: {result.stderr}")

            timeline = []
            current_time = 0.0
            for clip in clips:
                duration = self._get_duration(clip["output_file"])
                timeline.append({
                    "clip_id": clip["clip_id"],
                    "speaker": clip["speaker"],
                    "text": clip["text"],
                    "start_sec": round(current_time, 3),
                    "end_sec": round(current_time + duration, 3),
                })
                current_time += duration + (padding_ms / 1000.0)

            output = {
                "master_audio_path": str(master_path),
                "timeline": timeline,
                "total_duration_sec": round(current_time, 3),
                "clip_count": len(clips),
            }
            self.save("assembly.json", output)

            self.job_manager.update_status(
                self.project_id, job_id, "completed",
                result_path=str(master_path)
            )

            return {
                **output,
                "project_id": self.project_id,
                "job_id": job_id,
            }

        except Exception as e:
            self.job_manager.update_status(self.project_id, job_id, "failed", error_message=str(e))
            raise

    def _get_duration(self, file_path: str) -> float:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip()) if result.returncode == 0 else 0.0
