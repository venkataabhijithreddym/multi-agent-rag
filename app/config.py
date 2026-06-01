

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_chat_model: str = "gpt-4.1-mini"
    # Local embedding model (sentence-transformers, no API key needed)
    local_embedding_model: str = "multi-qa-MiniLM-L6-cos-v1"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # ChromaDB
    chroma_db_path: str = "./chroma_db"
    chroma_collection_name: str = "faqs"

    # FAQ data
    faq_data_path: str = "./data/faqs.xlsx"

    # SQLite
    database_url: str = "sqlite:///./app.db"

    # Weather (wttr.in)
    weather_city: str = "London"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()