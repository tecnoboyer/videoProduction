from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    PROJECTS_DIR: Path = Path("projects")
    OPENAI_API_KEY: str = ""
    AZURE_ID: str = ""
    ELEVENLAB_API_KEY: str = ""
    DASHSCOPE_KEY: str = ""
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_TTS_PROVIDER: str = "elevenlabs"
    DEFAULT_IMAGE_PROVIDER: str = "openai"
    DEFAULT_VIDEO_PROVIDER: str = "ffmpeg"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
