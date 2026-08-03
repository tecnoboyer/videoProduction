from pydantic import BaseModel, Field
from typing import Optional, List

class NarrativeInput(BaseModel):
    project_id: str
    raw_text: str = Field(..., description="Raw narrative text in natural storytelling form")
    style_hints: Optional[str] = ""
    target_duration_min: Optional[int] = None

class NarrativeOutput(BaseModel):
    project_id: str
    narrative_text: str
    summary: Optional[str] = ""
    characters: List[str] = []
    scenes_count: Optional[int] = None
    output_path: str
