from fastapi import APIRouter, HTTPException
from app.schemas.script import ScriptInput, ScriptOutput
from app.services.script.service import ScriptService
from app.services.project.manager import ProjectManager

router = APIRouter(prefix="/projects/{project_id}/script", tags=["Script - Block 1"])
manager = ProjectManager()

@router.post("/parse")
async def parse_script(project_id: str, payload: ScriptInput):
    try:
        project = manager.get_project(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

    service = ScriptService(project_id, manager.projects_dir / project_id)
    result = await service.generate(
        source=payload.source,
        raw_text=payload.raw_text,
        provider=project.get("llm_provider", "openai"),
    )

    manager.update_project(project_id, {
        "current_service": "script",
        "last_job_id": result["job_id"],
    })
    return result

@router.get("/output")
async def get_script_output(project_id: str):
    from pathlib import Path
    import json
    output_path = manager.projects_dir / project_id / "script" / "output" / "output.json"
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="No script output yet")
    return json.loads(output_path.read_text(encoding="utf-8"))
