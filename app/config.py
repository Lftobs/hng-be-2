from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str
    DB_HOST: str
    DB_PWD: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
