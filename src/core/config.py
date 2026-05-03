from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Settings
    api_title: str = "Sovereign RAG API"
    api_version: str = "0.1.0"
    
    # PostgreSQL / pgvector Settings (Defaults match our docker-compose)
    postgres_user: str = "admin"
    postgres_password: str = "secure_password_here"
    postgres_db: str = "sovereign_rag"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    
    # Redis Settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    # AI Model Settings
    embed_model_name: str = "BAAI/bge-small-en-v1.5"
    embed_dimension: int = 384
    
    # vLLM Settings (We will point this to our local OpenAI-compatible endpoint)
    vllm_base_url: str = "http://localhost:8000/v1" 
    llm_model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"

    # Pydantic Settings config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Instantiate a global settings object to be imported across the app
settings = Settings()