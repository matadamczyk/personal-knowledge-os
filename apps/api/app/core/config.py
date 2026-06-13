from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    database_url: str = "sqlite:///../../data/pkos.sqlite3"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "knowledge_items"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
