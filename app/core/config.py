import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_URL_ALEMBIC: str = os.getenv("DATABASE_URL_ALEMBIC")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")


    model_config = {"env_file": ".env"}

settings = Settings()