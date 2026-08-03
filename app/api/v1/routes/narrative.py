from fastapi import APIRouter, HTTPException
from app.schemas.narrative import NarrativeInput, NarrativeOutput
from app.services.narrative.service import NarrativeService
from app.services.project.manager import ProjectManager

router = APIRouter(prefix="/projects/{project_id}/narrative", tags=["Narrative"])
manager = ProjectManager()

@router.post("/generate")
async def generate_narrative(project_id: str, payload: NarrativeInput):
    try:
        project = manager.get_project(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

    service = NarrativeService(project_id, manager.projects_dir / project_id)
    result = await service.generate(
        raw_text=payload.raw_text,
        style_hints=payload.style_hints or "",
        provider=project.get("llm_provider", "openai"),
    )

    manager.update_project(project_id, {
        "current_service": "narrative",
        "last_job_id": result["job_id"],
    })

    return result

@router.get("/output")
async def get_narrative_output(project_id: str):
    try:
        project = manager.get_project(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

    import json
    from pathlib import Path
    output_path = manager.projects_dir / project_id / "narrative" / "output" / "output.json"
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="No narrative output yet")
    return json.loads(output_path.read_text(encoding="utf-8"))
