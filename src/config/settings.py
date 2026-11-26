from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "production"] = "development"

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:15432/concerts_afisha_db"
    )

    hash_scheme: Literal["argon2id"] = "argon2id"
    argon2_time_cost: int = Field(default=3, gt=0)
    argon2_memory_cost: int = Field(default=65536, gt=0)
    argon2_parallelism: int = Field(default=4, gt=0)

    admin_login: str
    admin_password: SecretStr
    secret_key: SecretStr

    port: int = Field(default=8000, gt=0, le=65535)