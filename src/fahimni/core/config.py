"""Application configuration loaded from environment variables via Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = Field(..., description="Async PostgreSQL DSN")

    # Redis / Celery
    redis_url: str = Field(default="redis://localhost:6379/0")

    # Auth
    secret_key: str = Field(..., description="JWT signing secret")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # HuggingFace / LangChain
    huggingface_model_id: str = "google/flan-t5-small"
    huggingface_api_token: str = Field(default="", description="HuggingFace API token")
    embedding_model_id: str = "BAAI/bge-small-en-v1.5"
    vector_store_path: str = ".chroma"

    # OCR
    tesseract_cmd: str | None = None

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "fahimni"
    minio_secure: bool = False

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # General
    log_level: str = "INFO"
    environment: str = "development"


settings = Settings()