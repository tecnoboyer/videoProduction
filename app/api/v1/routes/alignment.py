from fastapi import APIRouter, HTTPException
from app.schemas.alignment import AlignmentInput, AlignmentOutput
from app.services.alignment.service import AlignmentService
from app.services.project.manager import ProjectManager

router = APIRouter(prefix="/projects/{project_id}/alignment", tags=["Alignment - Block 4"])
manager = ProjectManager()

@router.post("/run")
async def run_alignment(project_id: str, payload: AlignmentInput):
    try:
        project = manager.get_project(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

    service = AlignmentService(project_id, manager.projects_dir / project_id)
    result = await service.generate(
        provider=payload.provider or "whisper",
        model=payload.model or "base",
        language=project.get("language", "es"),
    )
    manager.update_project(project_id, {
        "current_service": "alignment",
        "last_job_id": result["job_id"],
    })
    return result

@router.get("/output")
async def get_alignment_output(project_id: str):
    from pathlib import Path
    import json
    out = {}
    for name in ["alignment.json", "alignment.srt"]:
        p = manager.projects_dir / project_id / "alignment" / "output" / name
        if p.exists():
            if name.endswith(".json"):
                out[name.replace(".json", "")] = json.loads(p.read_text(encoding="utf-8"))
            else:
                out[name.replace(".", "_")] = p.read_text(encoding="utf-8")
    if not out:
        raise HTTPException(status_code=404, detail="No alignment output yet")
    return out
