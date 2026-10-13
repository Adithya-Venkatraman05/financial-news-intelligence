import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    marketaux_api_token = os.getenv("MARKETAUX_API_TOKEN")
    marketaux_base_url = "https://api.marketaux.com/v1/news/all"


settings = Settings()