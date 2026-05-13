"""Runtime configuration loaded from environment (PRD Section 10/11)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    deployment_mode: str = "cloud"          # cloud | airgapped

    embedding_model: str = "hashing"        # hashing | sentence-transformers
    embedding_dim: int = 384
    vector_backend: str = "memory"          # memory | qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "dlkip_chunks"

    llm_provider: str = "fallback"          # fallback | openai | ollama
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # Retrieval
    top_k: int = 5
    confidence_threshold: float = 0.15      # below this -> "not found"
    chunk_size: int = 600                   # characters
    chunk_overlap: int = 80


settings = Settings()
