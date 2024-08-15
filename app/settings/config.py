import os
import typing
import mysql.connector
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    VERSION: str = "0.1.0"
    APP_TITLE: str = "Vue FastAPI Admin"
    PROJECT_NAME: str = "Vue FastAPI Admin"
    APP_DESCRIPTION: str = "Description"

    CORS_ORIGINS: typing.List = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: typing.List = ["*"]
    CORS_ALLOW_HEADERS: typing.List = ["*"]

    DEBUG: bool = True
    # mysql连接
    DB_URL: str = "mysql://root:123456@localhost:3306/api"
    DB_CONNECTIONS: dict = {
        "default": {
            "engine": "tortoise.backends.mysql",
            "db_url": DB_URL,
            "credentials": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "123456",
                "database": "api",
            },
        },
    }

    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    BASE_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))
    LOGS_ROOT: str = os.path.join(BASE_DIR, "app/logs")
    SECRET_KEY: str = "3488a63e1765035d386f05409663f55c83bfae3b3c61a932744b20ad14244dcf"  # openssl rand -hex 32
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 24 * 7  # 7 day
    TORTOISE_ORM: dict = {
        "connections": {
            "default": {
                "engine": "tortoise.backends.mysql",
                "credentials": {
                    "host": "localhost",
                    "port": 3306,
                    "user": "root",
                    "password": "123456",
                    "database": "api",
                    "minsize": 1,
                    "maxsize": 5,
                    "echo": True
                },
            }
        },
        "apps": {
            "models": {
                "models": ["app.models"],
                "default_connection": "default",
            },
        },
        "use_tz": False,
        "timezone": "Asia/Shanghai",
    }
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

# Instantiate the settings
settings = Settings()
