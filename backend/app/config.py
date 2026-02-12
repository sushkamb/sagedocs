from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "openai"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_model: str = "gpt-5.2"
    llm_model_fast: str = "gpt-5-mini"  # Cost-effective model for high-volume help queries
    embedding_model: str = "text-embedding-3-small"

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma"

    # Server
    host: str = "0.0.0.0"
    port: int = 8500

    # CORS
    cors_origins: str = "http://localhost,http://localhost:8080"

    # Admin
    admin_secret_key: str = "change-this-to-a-random-string"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
