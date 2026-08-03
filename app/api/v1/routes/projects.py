from fastapi import APIRouter, HTTPException
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectStatus
from app.services.project.manager import ProjectManager
from app.services.job.manager import JobManager

router = APIRouter(prefix="/projects", tags=["Projects"])
manager = ProjectManager()
job_manager = JobManager()

@router.post("/", response_model=dict)
async def create_project(project: ProjectCreate):
    path = manager.create_project(
        title=project.title,
        description=project.description or "",
        language=project.language,
        voice=project.voice or "Rachel",
        image_model=project.image_model or "dall-e-3",
        video_model=project.video_model or "ffmpeg",
        llm_provider=project.llm_provider or "openai",
        metadata=project.metadata,
    )
    return {
        "message": "Project created",
        "project_id": manager.get_project(path.name)["id"],
        "path": str(path),
    }

@router.get("/")
async def list_projects():
    return manager.list_projects()

@router.get("/{project_id}")
async def get_project(project_id: str):
    try:
        return manager.get_project(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

@router.get("/{project_id}/status")
async def project_status(project_id: str):
    try:
        meta = manager.get_project(project_id)
        return ProjectStatus(
            project_id=project_id,
            status=meta.get("status", "unknown"),
            current_scene=meta.get("current_scene"),
            current_service=meta.get("current_service"),
            last_job_id=meta.get("last_job_id"),
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

@router.get("/{project_id}/jobs")
async def list_project_jobs(project_id: str, service: str = None):
    try:
        return job_manager.list_jobs(project_id, service_name=service)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

@router.get("/{project_id}/jobs/{job_id}")
async def get_job(project_id: str, job_id: str):
    try:
        return job_manager.get_job(project_id, job_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Job not found")
