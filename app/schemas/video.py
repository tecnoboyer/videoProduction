from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class SceneComposition(BaseModel):
    scene_id: str
    start_ms: int
    end_ms: int
    active_speaker: Optional[str] = None
    background_image: Optional[str] = None
    subtitle_text: Optional[str] = None
    subtitle_style: Optional[Dict[str, Any]] = {}
    effects: Optional[List[str]] = []

class SceneBuilderInput(BaseModel):
    project_id: str
    composition_style: Optional[str] = "default"

class SceneBuilderOutput(BaseModel):
    project_id: str
    scenes: List[SceneComposition]
    manifest_path: str

class VideoRenderInput(BaseModel):
    project_id: str
    engine: Optional[str] = "ffmpeg"
    resolution: Optional[str] = "1920x1080"
    fps: Optional[int] = 24

class VideoRenderOutput(BaseModel):
    project_id: str
    video_path: str
    duration_sec: float
    resolution: str
