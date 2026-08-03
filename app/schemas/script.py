from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class DialogueEvent(BaseModel):
    speaker: str
    text: str
    voice_id: Optional[str] = None
    emotion: Optional[str] = None
    direction: Optional[str] = None
    scene_id: Optional[str] = None

class ScriptInput(BaseModel):
    project_id: str
    source: str = Field("narrative", description="Source of input: narrative, raw, file")
    raw_text: Optional[str] = None
    file_path: Optional[str] = None

class ScriptOutput(BaseModel):
    project_id: str
    dialogue: List[DialogueEvent]
    scene_breakdown: Optional[List[Dict[str, Any]]] = []
    output_path: str
    clip_count: int
