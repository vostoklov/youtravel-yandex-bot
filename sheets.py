"""
Работа с Google Sheets
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SheetsManager:
    def __init__(self):
        self.client = None
        self.emails_sheet = None
        self.promos_sheet = None
    
    def connect(self):
        """Подключение к Google Sheets"""
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                config.GOOGLE_CREDENTIALS_JSON, scope
            )
            self.client = gspread.authorize(creds)
            
            # Открываем таблицы
            self.emails_sheet = self.client.open_by_key(config.GOOGLE_SHEET_EMAILS_ID).sheet1
            self.promos_sheet = self.client.open_by_key(config.GOOGLE_SHEET_PROMOS_ID).sheet1
            
            logger.info("✅ Connected to Google Sheets")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Google Sheets: {e}")
            raise
    
    def check_email_exists(self, email: str) -> bool:
        """Проверить наличие email в базе YouTravel"""
        try:
            # Получаем все email'ы из первого столбца (кроме заголовка)
            emails = self.emails_sheet.col_values(1)[1:]  # Skip header
            normalized_email = email.lower().strip()
            
            # Проверяем наличие
            return normalized_email in [e.lower().strip() for e in emails]
        except Exception as e:
            logger.error(f"Error checking email: {e}")
            return False
    
    def get_available_promo(self) -> Optional[str]:
        """Получить доступный промокод"""
        try:
            # Получаем все промокоды и статусы
            promos = self.promos_sheet.get_all_records()
            
            # Ищем первый неиспользованный
            for i, promo in enumerate(promos, start=2):  # start=2 т.к. строка 1 - заголовок
                if promo.get('is_used') == 'FALSE':
                    # Помечаем как использованный
                    self.promos_sheet.update_cell(i, 2, 'TRUE')
                    return promo.get('promo_code')
            
            logger.warning("⚠️ No available promo codes!")
            return None
        except Exception as e:
            logger.error(f"Error getting promo code: {e}")
            return None

# Глобальный инстанс
sheets = SheetsManager()
