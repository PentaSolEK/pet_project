from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # игнорировать лишние переменные из .env
    )

    database_url: str | None = None
    db_user: str | None = None
    db_password: str | None = None
    db_host: str | None = None
    db_name: str | None = None

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Rabbit
    rabbitmq_url: str = "amqp://guest:guest@localhost/"

    # CORS
    cors_allow_origins: list[str] = ["*"]

    # Email (SMTP)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    email_from: str | None = None

    @model_validator(mode="before")
    @classmethod
    def build_database_url(cls, data: dict | object) -> dict | object:
        if not isinstance(data, dict):
            return data
        if data.get("database_url"):
            return data
        if all((data.get("db_user"), data.get("db_host"), data.get("db_name"))):
            user = data["db_user"]
            password = data.get("db_password") or ""
            host = data["db_host"]
            name = data["db_name"]
            data = {**data, "database_url": f"mysql+asyncmy://{user}:{password}@{host}/{name}"}
        else:
            data = {**data, "database_url": data.get("database_url") or "mysql+asyncmy://localhost/local"}
        return data


settings = Settings()