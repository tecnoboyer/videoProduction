from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class TTSClip(BaseModel):
    clip_id: str
    speaker: str
    text: str
    voice_id: str
    emotion: Optional[str] = None
    output_file: Optional[str] = None
    duration_sec: Optional[float] = None

class TTSInput(BaseModel):
    project_id: str
    provider: Optional[str] = "elevenlabs"
    voice_settings: Optional[Dict] = {}
    clips: Optional[List[TTSClip]] = None

class TTSOutput(BaseModel):
    project_id: str
    clips: List[TTSClip]
    clips_dir: str

class AudioAssemblyInput(BaseModel):
    project_id: str
    padding_ms: int = 300
    normalize: bool = True

class AudioAssemblyOutput(BaseModel):
    project_id: str
    master_audio_path: str
    timeline: List[Dict]
    total_duration_sec: float
