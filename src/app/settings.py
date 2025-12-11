import os

from pydantic import BaseModel


class Settings(BaseModel):
    APP_NAME: str = os.getenv("APP_NAME", "Shoply")
    DEBUG: bool = os.getenv("DEBUG", "1") == "1"
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASS: str = os.getenv("DB_PASS", "")
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_NAME: str = os.getenv("DB_NAME", "shoply_db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
    ACCESS_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_EXPIRE_MINUTES", "15"))
    REFRESH_EXPIRE_DAYS: int = int(os.getenv("REFRESH_EXPIRE_DAYS", "30"))

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
