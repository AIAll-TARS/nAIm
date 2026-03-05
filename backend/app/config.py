from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://naim:naim@localhost:5432/naim"
    api_keys: list[str] = []
    environment: str = "development"
    log_level: str = "INFO"
    rating_pepper: str = "change-me-in-production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @field_validator("api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, v):
        if isinstance(v, str):
            return [k.strip() for k in v.split(",") if k.strip()]
        return v


settings = Settings()
