from fastapi import FastAPI
from app.api.v1 import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Video Creation Manager API",
    description="Motor AI modular para produccion de video con pipeline de 6 bloques",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok", "projects_dir": str(settings.PROJECTS_DIR)}
