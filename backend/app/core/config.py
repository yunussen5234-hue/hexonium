from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hexonium"
    environment: str = "development"
    secret_key: str = "super-secret-key"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 60 * 24 * 7
    database_url: str = "postgresql+psycopg2://hexonium:hexonium@localhost:5432/hexonium"
    iban_encryption_key: str = "jF8m8wJxY6R2gJ8sFQpo4YHc_8j9nY3kQj3v0v8P7Q4="

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
