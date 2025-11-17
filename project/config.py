from flask.cli import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()

class MailConfig(BaseSettings):
    MAIL_SERVER: str = Field(default='smtp.gmail.com', env='MAIL_SERVER')
    MAIL_PORT: int = Field(default=587, env='MAIL_PORT')
    MAIL_USE_TLS: bool = Field(default=True, env='MAIL_USE_TLS')
    MAIL_USERNAME: str = Field(default='your@email.com', env='MAIL_USERNAME')
    MAIL_PASSWORD: str = Field(default='your-password', env='MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER: str = Field(default='noreply@example.com', env='MAIL_DEFAULT_SENDER')
    MAIL_TOKEN_EXPIRE_HOURS: int = Field(default=24, env='MAIL_TOKEN_EXPIRE_HOURS')

class Settings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRES: int

    USER: str
    PASSWORD: str
    HOST_NAME: str
    DB_NAME: str
    PORT: str
    BOT_TOKEN: str
    CHANNEL_ID_KAZAN: str
    DEBUG_RESPONSE: bool # если true, то при ошибках будет выводить в response traceback и саму ошибку
    CHANNEL_ID_CHELNY: str
    CODE_EXPIRES: int #  в минутах

    REDIS_HOST_NAME: str
    REDIS_PORT: str
    REDIS_PASSWORD: str

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"

mail_config = MailConfig()
settings = Settings()
