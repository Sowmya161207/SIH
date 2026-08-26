import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings loaded from environment variables or .env file."""

    APP_NAME: str = "Sovereign AI Workbench"
    DEBUG: bool = True
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 20
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    OLLAMA_MODEL: str = "llama3.1:8b"
    OLLAMA_CODE_MODEL: str = "codellama:7b"
    OLLAMA_VISION_MODEL: str = "llava:7b"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    DEFAULT_TOP_K: int = 5
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    CHROMA_DB_DIR: str = "rag_vector_db"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated ALLOWED_ORIGINS into a list of strings."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        return self.ALLOWED_ORIGINS

    @property
    def max_file_size_bytes(self) -> int:
        """Convert MAX_FILE_SIZE_MB into bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


settings = Settings()
