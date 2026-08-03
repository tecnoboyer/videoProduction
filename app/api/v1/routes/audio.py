from fastapi import APIRouter, HTTPException
from app.schemas.audio import TTSInput, TTSOutput, AudioAssemblyInput, AudioAssemblyOutput
from app.services.audio.tts_service import TTSService
from app.services.audio.assembler import AudioAssembler
from app.services.project.manager import ProjectManager

router = APIRouter(prefix="/projects/{project_id}/audio", tags=["Audio - Blocks 2 & 3"])
manager = ProjectManager()

@router.post("/tts")
async def generate_tts(project_id: str, payload: TTSInput):
    try:
        project = manager.get_project(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

    service = TTSService(project_id, manager.projects_dir / project_id)
    result = await service.generate(
        provider=payload.provider or project.get("voice", "elevenlabs"),
        voice_settings=payload.voice_settings,
        clips=payload.clips,
    )
    manager.update_project(project_id, {
        "current_service": "audio_tts",
        "last_job_id": result["job_id"],
    })
    return result

@router.post("/assemble")
async def assemble_audio(project_id: str, payload: AudioAssemblyInput):
    try:
        project = manager.get_project(project_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

    service = AudioAssembler(project_id, manager.projects_dir / project_id)
    result = await service.generate(
        padding_ms=payload.padding_ms,
        normalize=payload.normalize,
    )
    manager.update_project(project_id, {
        "current_service": "audio_assembler",
        "last_job_id": result["job_id"],
    })
    return result

@router.get("/output")
async def get_audio_output(project_id: str):
    from pathlib import Path
    import json
    out = {}
    for name in ["tts_manifest.json", "assembly.json"]:
        p = manager.projects_dir / project_id / "audio" / "output" / name
        if p.exists():
            out[name.replace(".json", "")] = json.loads(p.read_text(encoding="utf-8"))
    if not out:
        raise HTTPException(status_code=404, detail="No audio output yet")
    return out
