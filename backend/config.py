from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./image_morph.db"
    
    # Cloudflare R2
    R2_ENDPOINT_URL: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "image-morph"
    R2_PUBLIC_URL: str = ""
    
    # Application
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://localhost:5500"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def _parse_debug(cls, value):
        if isinstance(value, bool) or value is None:
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            truthy = {"1", "true", "yes", "y", "on", "debug", "dev", "development"}
            falsy = {"0", "false", "no", "n", "off", "release", "prod", "production"}
            if normalized in truthy:
                return True
            if normalized in falsy:
                return False
        raise ValueError(
            "DEBUG must be a boolean (true/false) or a supported environment label "
            "(debug/dev/development/release/prod/production)."
        )


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
