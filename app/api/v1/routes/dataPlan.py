from fastapi import APIRouter

router = APIRouter(prefix="/projects/{project_id}/dataplan", tags=["Data Plan"])

@router.get("/status")
async def dataplan_status(project_id: str):
    return {"project_id": project_id, "status": "not_implemented", "message": "Data plan module placeholder"}
