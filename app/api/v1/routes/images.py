from fastapi import APIRouter, HTTPException
from app.schemas.image import ImageInput, ImageOutput
from app.services.providers.factory import ProviderFactory
from app.services.project.manager import ProjectManager
from app.services.job.manager import JobManager
import json

router = APIRouter(prefix="/projects/{project_id}/images", tags=["Images"])
manager = ProjectManager()
job_manager = JobManager()

@router.post("/generate")
async def generate_images(project_id: str, payload: ImageInput):
    try:
        project = manager.get_project(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

    job_id = job_manager.create_job(
        project_id=project_id,
        service_name="images",
        provider=payload.provider or project.get("image_model", "openai"),
    )
    job_manager.update_status(project_id, job_id, "running")

    try:
        provider = ProviderFactory.get_image(payload.provider or "openai")
        output_dir = manager.projects_dir / project_id / "images" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        prompts = payload.prompts or []
        images = []
        for i, p in enumerate(prompts):
            out_file = output_dir / f"{p.prompt_id or f'img_{i:03d}'}.png"
            await provider.generate_image(
                prompt=p.prompt,
                output_path=str(out_file),
                size=p.size or "1024x1024",
            )
            images.append({"prompt_id": p.prompt_id, "path": str(out_file)})

        job_manager.update_status(project_id, job_id, "completed", result_path=str(output_dir))
        manager.update_project(project_id, {"current_service": "images", "last_job_id": job_id})

        return {
            "project_id": project_id,
            "images": images,
            "output_dir": str(output_dir),
            "job_id": job_id,
        }
    except Exception as e:
        job_manager.update_status(project_id, job_id, "failed", error_message=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/output")
async def get_images_output(project_id: str):
    from pathlib import Path
    output_dir = manager.projects_dir / project_id / "images" / "output"
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="No images output yet")
    return {"images": [str(f) for f in sorted(output_dir.glob("*")) if f.suffix in (".png", ".jpg", ".webp")]}
