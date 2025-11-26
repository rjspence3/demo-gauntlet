import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Config:
    PROJECT_NAME = "Demo Gauntlet"
    VERSION = "0.1.0"
    # Placeholder for future config
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Feature Flags
    ENABLE_RESEARCH: bool = True
    MAX_CHALLENGERS: int = 3
    
    # Security
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    
    model_config = SettingsConfigDict(env_file=".env")

config = Config()
