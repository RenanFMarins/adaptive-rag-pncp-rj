from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: SecretStr = SecretStr("")
    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=30, gt=0, le=10080)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
