# core/config.py
from dataclasses import dataclass
import os

@dataclass
class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "SIDO Inventory")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/app.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-please")
    # Service level target: z for 95% ≈ 1.65 (used in safety stock calc)
    SERVICE_LEVEL_Z: float = float(os.getenv("SERVICE_LEVEL_Z", "1.65"))
    USAGE_WINDOW_DAYS: int = int(os.getenv("USAGE_WINDOW_DAYS", "90"))
    COMPANY_NAME: str = os.getenv("COMPANY_NAME", "Sido Digital Print Solutions Ltd.")
    COMPANY_ADDRESS: str = os.getenv("COMPANY_ADDRESS", "Plot M799 Spring Road Bugolobi, Kampala")
    COMPANY_PHONE: str = os.getenv("COMPANY_PHONE", "+256782947295 / 0779520887")
    COMPANY_EMAIL: str = os.getenv("COMPANY_EMAIL", "sales@sidps.com")

settings = Settings()
