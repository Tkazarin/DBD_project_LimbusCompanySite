import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file="secret.env"
    )


settings = Settings()


def get_auth_data():
    return {"secret_key": settings.SECRET_KEY, "algorithm": settings.ALGORITHM}


def get_database_url():
    return settings.DATABASE_URL
