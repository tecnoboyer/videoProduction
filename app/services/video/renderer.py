"""Block 6: Video Renderer.
Renders final MP4 from scene manifest + master audio."""
import json
import subprocess
from pathlib import Path
from typing import Any, Optional
from app.services.base_service import BaseService
from app.services.job.manager import JobManager

class VideoRenderer(BaseService):
    service_name = "video"

    def __init__(self, project_id: str, project_path: Path):
        super().__init__(project_id, project_path)
        self.job_manager = JobManager()
        self.renders_dir = self.output_dir / "renders"
        self.renders_dir.mkdir(parents=True, exist_ok=True)

    def validate(self, data: Any) -> bool:
        return isinstance(data, dict) and "scenes" in data

    async def generate(
        self,
        engine: str = "ffmpeg",
        resolution: str = "1920x1080",
        fps: int = 24,
        **kwargs: Any
    ) -> dict:
        job_id = self.job_manager.create_job(
            project_id=self.project_id,
            service_name=self.service_name,
            provider=engine,
            input_folder=str(self.input_dir),
            output_folder=str(self.output_dir),
        )
        self.job_manager.update_status(self.project_id, job_id, "running")

        try:
            manifest_path = self.project_path / "scenes" / "output" / "scene_manifest.json"
            audio_path = self.project_path / "audio" / "output" / "master_audio.wav"

            if not manifest_path.exists():
                raise FileNotFoundError("No scene manifest found. Run Scene Builder first.")
            if not audio_path.exists():
                raise FileNotFoundError("No master audio found. Run Audio Assembler first.")

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            scenes = manifest["scenes"]

            output_video = self.renders_dir / "final_video.mp4"

            for i, scene in enumerate(scenes):
                img = scene.get("background_image")
                if not img or not Path(img).exists():
                    img = str(self.input_dir / f"blank_{i}.png")
                    subprocess.run([
                        "ffmpeg", "-y", "-f", "lavfi", "-i",
                        f"color=c=black:s={resolution}", "-frames:v", "1", img
                    ], capture_output=True)

            concat_script = self.input_dir / "video_concat.txt"
            with open(concat_script, "w") as f:
                for i, scene in enumerate(scenes):
                    duration = (scene["end_ms"] - scene["start_ms"]) / 1000.0
                    img = scene.get("background_image")
                    if not img or not Path(img).exists():
                        img = str(self.input_dir / f"blank_{i}.png")
                    f.write(f"file '{img}'\nduration {duration}\n")
                last_img = scenes[-1].get("background_image")
                if not last_img or not Path(last_img).exists():
                    last_img = str(self.input_dir / f"blank_{len(scenes)-1}.png")
                f.write(f"file '{last_img}'\n")

            temp_video = self.output_dir / "temp_video.mp4"
            cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(concat_script),
                "-vf", f"fps={fps},format=yuv420p,scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-shortest",
                str(temp_video)
            ]
            subprocess.run(cmd, capture_output=True, check=True)

            cmd = [
                "ffmpeg", "-y",
                "-i", str(temp_video),
                "-i", str(audio_path),
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                str(output_video)
            ]
            subprocess.run(cmd, capture_output=True, check=True)

            duration = self._get_duration(str(output_video))

            self.job_manager.update_status(
                self.project_id, job_id, "completed",
                result_path=str(output_video)
            )

            return {
                "project_id": self.project_id,
                "video_path": str(output_video),
                "duration_sec": duration,
                "resolution": resolution,
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
