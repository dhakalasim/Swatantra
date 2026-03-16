import os
from enum import Enum
from pydantic_settings import BaseSettings
from functools import lru_cache


class DBType(str, Enum):
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"


class Settings(BaseSettings):
    """Application configuration with support for online (PostgreSQL) and offline (SQLite) modes"""
    
    # Core settings
    APP_NAME: str = "Swatantra"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database settings
    DB_TYPE: DBType = DBType(os.getenv("DB_TYPE", "sqlite"))
    
    # PostgreSQL settings (for cloud deployment)
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "swatantra")
    
    # SQLite settings (for offline/local development)
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "./data/swatantra.db")
    
    # API Configuration
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost", "*"]
    
    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))
    
    # Offline LLM settings (Ollama fallback)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    USE_OFFLINE_LLM: bool = os.getenv("USE_OFFLINE_LLM", "False").lower() == "true"
    OFFLINE_LLM_MODEL: str = os.getenv("OFFLINE_LLM_MODEL", "mistral")
    
    # Agent settings
    MAX_AGENT_ITERATIONS: int = int(os.getenv("MAX_AGENT_ITERATIONS", "10"))
    AGENT_TIMEOUT_SECONDS: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "300"))
    
    # AWS settings
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def database_url(self) -> str:
        """Generate database URL based on configuration"""
        if self.DB_TYPE == DBType.POSTGRESQL:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:  # SQLite
            return f"sqlite:///{self.SQLITE_DB_PATH}"
    
    def is_offline_mode(self) -> bool:
        """Check if running in offline mode"""
        return self.DB_TYPE == DBType.SQLITE or self.USE_OFFLINE_LLM


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
