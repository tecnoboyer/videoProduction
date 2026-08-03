from fastapi import APIRouter

router = APIRouter(prefix="/projects/{project_id}/post", tags=["Post-Production"])

@router.get("/status")
async def post_status(project_id: str):
    return {"project_id": project_id, "status": "not_implemented", "message": "Post-production module placeholder"}
