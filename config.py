from pydantic import BaseSettings
from functools import lru_cache

import os


class Settings(BaseSettings):
    app_name: str = "Redis test"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
