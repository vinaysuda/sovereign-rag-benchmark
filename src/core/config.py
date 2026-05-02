from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database Settings
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "securepassword"
    POSTGRES_DB: str = "sovereign_rag"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Inference & Embeddings (The Sovereign Boundary)
    # vLLM exposes an API that perfectly mimics OpenAI, so we can use standard tooling
    VLLM_API_BASE: str = "http://localhost:8000/v1"
    VLLM_MODEL_NAME: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"

    # Observability (Placeholders for now)
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()