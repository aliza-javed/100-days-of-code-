from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production-access-key"
    JWT_REFRESH_SECRET: str = "change-me-in-production-refresh-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MIN: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    PROJECT_NAME: str = "Day 3 JWT Auth"
    VERSION: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
