import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
import os
import json
import config

logger = logging.getLogger(__name__)


class SheetsManager:
    """Менеджер для работы с Google Sheets"""
    
    def __init__(self):
        self.client = None
        self.worksheet = None
        
    def connect(self):
        """Подключение к Google Sheets"""
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
            self.client = gspread.authorize(creds)
            
            # Открываем таблицу с email
            spreadsheet = self.client.open_by_key(config.GOOGLE_SHEET_EMAILS_ID)
            self.worksheet = spreadsheet.sheet1
            
            logger.info("✅ Connected to Google Sheets")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Google Sheets: {e}")
            raise
    
    def check_email_exists(self, email: str) -> bool:
        """Проверка существования email в таблице YouTravel"""
        try:
            # Получаем все email из колонки A (пропускаем заголовок)
            emails = self.worksheet.col_values(1)[1:]
            return email.lower() in [e.lower() for e in emails if e]
        except Exception as e:
            logger.error(f"Error checking email: {e}")
            return False
    
    def get_available_promo(self) -> str:
        """Получить доступный промокод из таблицы"""
        try:
            # Получаем все промокоды из колонки B (пропускаем заголовок)
            promo_codes = self.worksheet.col_values(2)[1:]
            
            # Возвращаем первый непустой промокод
            for promo in promo_codes:
                if promo and promo.strip():
                    return promo.strip()
            
            return None
        except Exception as e:
            logger.error(f"Error getting promo code: {e}")
            return None


# Глобальный экземпляр
sheets = SheetsManager()
