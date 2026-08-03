from pydantic import BaseModel, Field
from typing import List, Optional

class WordTimestamp(BaseModel):
    word: str
    start_ms: int
    end_ms: int
    speaker: Optional[str] = None

class AlignmentInput(BaseModel):
    project_id: str
    provider: Optional[str] = "whisper"
    model: Optional[str] = "base"

class AlignmentOutput(BaseModel):
    project_id: str
    words: List[WordTimestamp]
    srt_path: str
    json_path: str
