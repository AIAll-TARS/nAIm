from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://naim:naim@localhost:5432/naim"
    api_keys: list[str] = []  # loaded from env as comma-separated string
    environment: str = "development"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def parse_api_keys(self, raw: str) -> list[str]:
        return [k.strip() for k in raw.split(",") if k.strip()]


settings = Settings()
