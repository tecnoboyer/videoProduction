from fastapi import APIRouter, HTTPException
from app.schemas.video import SceneBuilderInput, SceneBuilderOutput
from app.services.scenes.builder import SceneBuilder
from app.services.project.manager import ProjectManager

router = APIRouter(prefix="/projects/{project_id}/scenes", tags=["Scenes - Block 5"])
manager = ProjectManager()

@router.post("/build")
async def build_scenes(project_id: str, payload: SceneBuilderInput):
    try:
        project = manager.get_project(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

    service = SceneBuilder(project_id, manager.projects_dir / project_id)
    result = await service.generate(
        composition_style=payload.composition_style or "default",
    )
    manager.update_project(project_id, {
        "current_service": "scenes",
        "last_job_id": result["job_id"],
    })
    return result

@router.get("/output")
async def get_scenes_output(project_id: str):
    from pathlib import Path
    import json
    p = manager.projects_dir / project_id / "scenes" / "output" / "scene_manifest.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail="No scene manifest yet")
    return json.loads(p.read_text(encoding="utf-8"))
