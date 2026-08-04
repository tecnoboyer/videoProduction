"""Block 6: Video Renderer.
Renders final MP4 from scene manifest + master audio."""
import json
import subprocess
import shutil
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

    def _run_ffmpeg(self, cmd: list, step_name: str) -> None:
        """Run ffmpeg with detailed error reporting."""
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            err = result.stderr[-800:] if result.stderr else "No stderr output"
            raise RuntimeError(
                f"FFmpeg failed at step '{step_name}' (code {result.returncode}):\n"
                f"Command: {' '.join(str(c) for c in cmd)}\n"
                f"Stderr: {err}"
            )

    def _copy_or_convert_image(self, src: Path, dst: Path, resolution: str) -> None:
        """Copy image if already correct size, or convert with ffmpeg."""
        if not src.exists():
            raise FileNotFoundError(f"Source image not found: {src}")

        # Try simple copy first (faster, avoids ffmpeg issues)
        try:
            shutil.copy2(src, dst)
            return
        except Exception:
            pass

        # Fallback: use ffmpeg with simple, safe filter
        # Use "scale=1920:1080" instead of complex pad expression
        w, h = resolution.split("x")
        cmd = [
            "ffmpeg", "-y",
            "-i", str(src),
            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:-1:-1:black",
            "-frames:v", "1",
            str(dst)
        ]
        self._run_ffmpeg(cmd, f"convert_image_{src.name}")

    def _create_blank_frame(self, path: Path, resolution: str) -> None:
        """Create a black frame."""
        w, h = resolution.split("x")
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=black:s={w}x{h}",
            "-frames:v", "1",
            str(path)
        ]
        self._run_ffmpeg(cmd, "blank_frame")

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
            # 1. Load inputs
            manifest_path = self.project_path / "scenes" / "output" / "scene_manifest.json"
            audio_path = self.project_path / "audio" / "output" / "master_audio.wav"

            if not manifest_path.exists():
                raise FileNotFoundError("No scene manifest found. Run Scene Builder first.")
            if not audio_path.exists():
                raise FileNotFoundError("No master audio found. Run Audio Assembler first.")

            manifest = self._safe_read_json(manifest_path)
            scenes = manifest.get("scenes", []) if isinstance(manifest, dict) else []
            if not scenes:
                raise ValueError("Scene manifest has no scenes")

            output_video = self.renders_dir / "final_video.mp4"

            # 2. Prepare frames directory
            frames_dir = self.input_dir / "frames"
            frames_dir.mkdir(parents=True, exist_ok=True)

            frame_files = []
            for i, scene in enumerate(scenes):
                img_path = scene.get("background_image")
                frame_dst = frames_dir / f"frame_{i:03d}.png"

                if img_path and Path(img_path).exists():
                    self._copy_or_convert_image(Path(img_path), frame_dst, resolution)
                else:
                    self._create_blank_frame(frame_dst, resolution)

                frame_files.append(frame_dst)

            # 3. Build concat script with relative forward-slash paths
            concat_script = self.input_dir / "concat.txt"
            with open(concat_script, "w", encoding="utf-8") as f:
                for i, (scene, frame) in enumerate(zip(scenes, frame_files)):
                    duration = max(0.5, (scene["end_ms"] - scene["start_ms"]) / 1000.0)
                    rel = frame.relative_to(concat_script.parent).as_posix()
                    f.write(f"file '{rel}'\n")
                    f.write(f"duration {duration}\n")
                # Repeat last frame
                last_rel = frame_files[-1].relative_to(concat_script.parent).as_posix()
                f.write(f"file '{last_rel}'\n")

            # 4. Concatenate frames into video
            temp_video = self.output_dir / "temp_video.mp4"
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_script),
                "-vf", f"fps={fps},format=yuv420p",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                str(temp_video)
            ]
            self._run_ffmpeg(cmd, "concat_video")

            # 5. Add audio
            cmd = [
                "ffmpeg", "-y",
                "-i", str(temp_video),
                "-i", str(audio_path),
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                str(output_video)
            ]
            self._run_ffmpeg(cmd, "add_audio")

            # 6. Get duration
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

    def _safe_read_json(self, file_path: Path) -> Any:
        """Safely read JSON with fallback for single-quoted files."""
        import json
        content = file_path.read_text(encoding="utf-8").strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            if "'" in content and '"' not in content:
                cleaned = content.replace("'", '"')
                return json.loads(cleaned)
            raise

    def _get_duration(self, file_path: str) -> float:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip()) if result.returncode == 0 else 0.0
