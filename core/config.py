import os

class Settings:
    APP_NAME = "Web-Putty Backend"
    SSH_CONNECTION_TIMEOUT = int(os.getenv("SSH_TIMEOUT", 10))
    MAX_SSH_SESSIONS = int(os.getenv("MAX_SSH_SESSIONS", 10))

settings = Settings()