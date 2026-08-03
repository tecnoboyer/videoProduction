from pydantic import BaseModel, Field
from typing import Optional, List

class ImagePrompt(BaseModel):
    prompt_id: str
    scene_id: Optional[str] = None
    prompt: str
    negative_prompt: Optional[str] = ""
    style: Optional[str] = ""
    size: Optional[str] = "1024x1024"

class ImageInput(BaseModel):
    project_id: str
    provider: Optional[str] = "openai"
    prompts: Optional[List[ImagePrompt]] = None

class ImageOutput(BaseModel):
    project_id: str
    images: List[dict]
    output_dir: str
