from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Project title / episode name")
    description: Optional[str] = ""
    language: str = "es"
    voice: Optional[str] = "Rachel"
    image_model: Optional[str] = "dall-e-3"
    video_model: Optional[str] = "ffmpeg"
    llm_provider: Optional[str] = "openai"
    metadata: Optional[Dict[str, Any]] = {}

class ProjectResponse(BaseModel):
    id: str
    title: str
    path: str
    status: str = "created"
    created_at: datetime
    metadata: Dict[str, Any]

class ProjectStatus(BaseModel):
    project_id: str
    status: str
    current_scene: Optional[int] = None
    current_service: Optional[str] = None
    last_job_id: Optional[str] = None
