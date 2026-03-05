from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://naim:naim@localhost:5432/naim"
    api_keys_raw: str = ""  # comma-separated string, set via API_KEYS_RAW env var
    environment: str = "development"
    log_level: str = "INFO"
    rating_pepper: str = "change-me-in-production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def api_keys(self) -> list[str]:
        return [k.strip() for k in self.api_keys_raw.split(",") if k.strip()]


settings = Settings()
