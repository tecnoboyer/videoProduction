from fastapi import APIRouter, HTTPException
from app.schemas.video import VideoRenderInput, VideoRenderOutput
from app.services.video.renderer import VideoRenderer
from app.services.project.manager import ProjectManager

router = APIRouter(prefix="/projects/{project_id}/video", tags=["Video - Block 6"])
manager = ProjectManager()

@router.post("/render")
async def render_video(project_id: str, payload: VideoRenderInput):
    try:
        project = manager.get_project(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

    service = VideoRenderer(project_id, manager.projects_dir / project_id)
    result = await service.generate(
        engine=payload.engine or project.get("video_model", "ffmpeg"),
        resolution=payload.resolution or "1920x1080",
        fps=payload.fps or 24,
    )
    manager.update_project(project_id, {
        "current_service": "video",
        "status": "completed",
        "last_job_id": result["job_id"],
    })
    return result

@router.get("/output")
async def get_video_output(project_id: str):
    from pathlib import Path
    p = manager.projects_dir / project_id / "video" / "output" / "renders" / "final_video.mp4"
    if not p.exists():
        raise HTTPException(status_code=404, detail="No video rendered yet")
    return {"video_path": str(p), "exists": True}
