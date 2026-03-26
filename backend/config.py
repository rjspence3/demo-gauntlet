"""
Configuration settings for the application.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Config(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """
    PROJECT_NAME: str = "Demo Gauntlet"
    VERSION: str = "0.1.0"
    
    # API Keys
    ANTHROPIC_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    BRAVE_API_KEY: str | None = None

    # Feature Flags
    ENABLE_RESEARCH: bool = True
    MAX_CHALLENGERS: int = 3
    
    # Security
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:8000"
    SECRET_KEY: str = "your-secret-key-please-change-in-prod"
    
    # ... (other fields)

    @property
    def is_production(self) -> bool:
        # Heuristic for production environment
        return os.getenv("ENV_MODE", "development").lower() == "production"

    def validate_security(self) -> None:
        """
        Validates critical security settings.
        Raises ValueError if configuration is insecure for production.
        Logs a loud warning in all other environments when the default key is active.
        """
        import logging
        # SECRET_KEY check always runs before any other production validation.
        if self.is_production:
            if self.SECRET_KEY == "your-secret-key-please-change-in-prod":
                logging.critical("SECURITY CRITICAL: Running in production with default SECRET_KEY! Application execution stopped.")
                raise ValueError("SECRET_KEY must be changed from default in production environment.")
            if not self.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY is required in production.")
        else:
            if self.SECRET_KEY == "your-secret-key-please-change-in-prod":
                logging.warning(
                    "SECURITY WARNING: SECRET_KEY is set to the insecure default value. "
                    "Set SECRET_KEY in your .env file before exposing this service externally."
                )

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BETA_INVITE_CODE: str | None = None # If set, requires this code to register
    
    # Storage (Placeholders for Phase 3)
    DATABASE_URL: str = "sqlite:///./data/app.db"
    BLOB_STORAGE_TYPE: str = "local" # local, s3
    
    # S3 Configuration
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    S3_BUCKET_NAME: str | None = None
    
    # Chroma Configuration
    CHROMA_PERSISTENCE_PATH: str = "./data/chroma_db"
    CHROMA_SERVER_HOST: str | None = None
    CHROMA_SERVER_PORT: int | None = None
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_KEY_PREFIX: str = "dg:"  # Unique prefix to avoid key collisions with other projects

    # DSPy Configuration
    # Set DSPY_PROGRAM_PATH to the path of a compiled GauntletAgent JSON file
    # to enable DSPy-optimized ideal answer generation.
    # Run backend/dspy_optimization/optimize.py to produce this file.
    DSPY_PROGRAM_PATH: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        
    def validate_production(self) -> None:
        """Validates configuration for production environment."""
        self.validate_security()

config = Config()
