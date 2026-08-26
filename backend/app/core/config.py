from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env."""

    APP_NAME: str = "Sovereign AI Workbench"
    DEBUG: bool = True

    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 200

    # Frontend CORS
    ALLOWED_ORIGINS: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )

    # RAG settings
    CHROMA_DB_DIR: str = "rag_vector_db"
    EMBEDDING_MODEL_NAME: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    EMBEDDING_DIM: int = 384
    CHUNK_SIZE: int = 400
    CHUNK_OVERLAP: int = 80
    DEFAULT_TOP_K: int = 5

    # On-Premise LLM / Ollama settings (100% Local - No Data Leakage)
    LLM_PROVIDER: str = "ollama"
    OLLAMA_URL: str = "http://127.0.0.1:11434/api/generate"
    OLLAMA_MODEL: str = "llama3.1:8b"
    LLM_TEMPERATURE: float = 0.1
    LLM_TIMEOUT_SECONDS: float = 120.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated CORS origins."""

        if isinstance(self.ALLOWED_ORIGINS, str):
            return [
                origin.strip()
                for origin in self.ALLOWED_ORIGINS.split(",")
                if origin.strip()
            ]

        return self.ALLOWED_ORIGINS

    @property
    def max_file_size_bytes(self) -> int:
        """Convert maximum upload size from MB to bytes."""

        return self.MAX_FILE_SIZE_MB * 1024 * 1024


settings = Settings()