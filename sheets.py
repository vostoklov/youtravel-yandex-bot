import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
import os
import json

logger = logging.getLogger(__name__)

def get_sheets_client():
    """Подключение к Google Sheets через credentials из переменной окружения"""
    try:
        # Читаем JSON напрямую из переменной окружения
        creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if not creds_json:
            raise ValueError("GOOGLE_CREDENTIALS_JSON not set")
        
        # Парсим JSON
        creds_dict = json.loads(creds_json)
        
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        logger.info("✅ Connected to Google Sheets")
        return client
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Google Sheets: {e}")
        raise

def get_worksheet(client, sheet_id: str, worksheet_name: str = None):
    """Получить worksheet по ID таблицы"""
    try:
        spreadsheet = client.open_by_key(sheet_id)
        if worksheet_name:
            return spreadsheet.worksheet(worksheet_name)
        return spreadsheet.sheet1
    except Exception as e:
        logger.error(f"❌ Failed to open worksheet: {e}")
        raise
