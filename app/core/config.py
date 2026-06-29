from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    OPENAI_API_KEY: str

    GEMINI_API_KEY: str

    PROJECTS_FOLDER: str = "./projects"

    class Config:
        env_file = ".env"


settings = Settings()