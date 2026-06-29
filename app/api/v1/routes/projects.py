from fastapi import APIRouter

from app.schemas.project import ProjectCreate
from app.services.project.manager import ProjectManager

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

@router.post("/")
async def create_project(project: ProjectCreate):

    manager = ProjectManager()

    path = manager.create_project(project.title)

    return {
        "message": "Project created",
        "path": str(path)
    }