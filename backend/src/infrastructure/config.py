from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "InkFig"
    environment: str = "local"
    database_url: str = "sqlite+aiosqlite:///./inkfig.db"
    supabase_url: AnyUrl | None = None
    supabase_publishable_key: str | None = None
    supabase_secret_key: str | None = None
    supabase_jwks_url: AnyUrl | None = None
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value


settings = Settings()
