from pydantic import BaseSettings

class Settings(BaseSettings):
    # Você pode definir variáveis via .env ou Google Secret Manager
    TELEGRAM_API_ID: int = 0
    TELEGRAM_API_HASH: str = ""
    LOG_LEVEL: str = "INFO"

settings = Settings()
