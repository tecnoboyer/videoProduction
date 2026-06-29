from fastapi import APIRouter

from app.services.narrative.service import NarrativeService

router = APIRouter()

@router.post("/generate")

def generate():

    service = NarrativeService()

    service.generate()

    return {"status":"ok"}