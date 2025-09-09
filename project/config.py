from flask.cli import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRES_HOURS: int

    USER: str
    PASSWORD: str
    HOST_NAME: str
    DB_NAME: str
    PORT: str
    BOT_TOKEN: str
    CHANNEL_ID: str

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"


settings = Settings()
