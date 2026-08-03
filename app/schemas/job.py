from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class JobCreate(BaseModel):
    project_id: str
    service_name: str
    provider: Optional[str] = None
    input_summary: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = {}

class JobResponse(BaseModel):
    job_id: str
    project_id: str
    service_name: str
    provider: Optional[str]
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    input_folder: Optional[str] = None
    output_folder: Optional[str] = None
    result_path: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any]
