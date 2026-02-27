from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    yutori_api_key: str = ""
    tavily_api_key: str = ""
    openai_api_key: str = ""
    alpha_vantage_api_key: str = ""
    
    # Neo4j
    neo4j_uri: str = ""
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # App
    environment: str = "development"
    log_level: str = "INFO"
    cache_ttl_seconds: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
