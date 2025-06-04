from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "3f3e19438aa2a38e07fee8b639e39312ebe77af29ef608a6eaeea35b2f5c3b0f"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///app.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()