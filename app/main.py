from fastapi import FastAPI
from app.api.v1.routes.projects import router as project_router

app = FastAPI(
    title="Video Production API",
    version="1.0.0",
    description="AI Assisted Video Production Backend"
)
app.include_router(project_router)
@app.get("/")
def root():
    return {
        "message": "Video Production API",
        "status": "running"
    }