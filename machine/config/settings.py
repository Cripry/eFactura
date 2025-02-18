from pydantic import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "PROD"
    BASE_TIMEOUT: int = 10
    POPUP_TIMEOUT: int = 6

    class Config:
        env_file = ".env"


settings = Settings()
