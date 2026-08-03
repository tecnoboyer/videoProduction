from fastapi import APIRouter
from app.api.v1.routes import projects, narrative, script, audio, images, alignment, scenes, video, postproduction, dataPlan

api_router = APIRouter()

api_router.include_router(projects.router)
api_router.include_router(narrative.router)
api_router.include_router(script.router)
api_router.include_router(audio.router)
api_router.include_router(images.router)
api_router.include_router(alignment.router)
api_router.include_router(scenes.router)
api_router.include_router(video.router)
api_router.include_router(postproduction.router)
api_router.include_router(dataPlan.router)
