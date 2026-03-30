from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "openai"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_model: str = "gpt-5.2"
    llm_model_fast: str = "gpt-5-mini"  # Cost-effective model for high-volume help queries
    embedding_model: str = "text-embedding-3-large"  # Higher quality embeddings for better retrieval

    # LLM Temperature
    help_temperature: float = 0.2  # Low temperature for factual help responses
    data_temperature: float = 0.5  # Moderate temperature for data formatting

    # RAG Pipeline
    chunk_size: int = 1200  # Larger chunks preserve more context per result
    chunk_overlap: int = 200
    rag_top_k: int = 8  # Final number of chunks sent to LLM
    rag_retrieval_k: int = 20  # Fetch more candidates for reranking
    similarity_threshold: float = 0.65  # Max cosine distance (0=identical, lower=stricter)

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma"

    # Logging
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8500

    # CORS
    cors_origins: str = "http://localhost,http://localhost:8080"

    # Admin
    admin_secret_key: str = "change-this-to-a-random-string"
    admin_username: str = "admin"
    admin_password: str = "change-this-password"
    jwt_secret: str = "change-this-jwt-secret"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
