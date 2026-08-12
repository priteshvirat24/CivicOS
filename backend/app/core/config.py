from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "postgresql://civicos_user:civicos_password@localhost:5432/civicos"
    poll_interval_seconds: int = 3600
    
    # Optional API keys for advanced normalization
    openai_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
