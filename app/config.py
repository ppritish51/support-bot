"""Central settings, loaded from environment / .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM (generation)
    anthropic_api_key: str = ""
    gen_model: str = "claude-haiku-4-5"

    # Embeddings
    openai_api_key: str = ""
    embed_model: str = "text-embedding-3-small"
    embed_dim: int = 1536  # text-embedding-3-small

    # Pinecone
    pinecone_api_key: str = ""
    pinecone_index: str = "support-deflector"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    # Retrieval / guardrail tuning
    top_k: int = 4
    conf_high: float = 0.50
    conf_medium: float = 0.35
    max_agent_iters: int = 4


settings = Settings()
