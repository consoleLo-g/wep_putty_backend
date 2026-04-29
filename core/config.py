import os
from dotenv import load_dotenv

load_dotenv()   

class Settings:
    APP_NAME = "WebPutty Backend"

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # Security
    APP_ACCESS_PASSWORD = os.getenv(
        "APP_ACCESS_PASSWORD",
        "ChangeThisPassword123"
    )

    TOKEN_EXPIRE_HOURS = int(
        os.getenv("TOKEN_EXPIRE_HOURS", 168)  # 7 days
    )

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-secret-key"
    )

    # MongoDB
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017"
    )

    DB_NAME = os.getenv(
        "DB_NAME",
        "webputty"
    )

    # SSH
    SSH_CONNECTION_TIMEOUT = int(
        os.getenv("SSH_TIMEOUT", 10)
    )

    MAX_SSH_SESSIONS = int(
        os.getenv("MAX_SSH_SESSIONS", 10)
    )


settings = Settings()