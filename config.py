"""
Конфигурация приложения
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Google Sheets
GOOGLE_SHEET_EMAILS_ID = os.getenv("GOOGLE_SHEET_EMAILS_ID")
GOOGLE_SHEET_PROMOS_ID = os.getenv("GOOGLE_SHEET_PROMOS_ID")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "credentials.json")

# Support
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "vostoklov")

# Admin
ADMIN_USER_IDS = [int(x) for x in os.getenv("ADMIN_USER_IDS", "201800866").split(",")]

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Validation
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не задан в .env")
if not GOOGLE_SHEET_EMAILS_ID:
    raise ValueError("GOOGLE_SHEET_EMAILS_ID не задан в .env")
if not GOOGLE_SHEET_PROMOS_ID:
    raise ValueError("GOOGLE_SHEET_PROMOS_ID не задан в .env")
