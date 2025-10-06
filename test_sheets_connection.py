#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к Google Sheets
"""
import logging
from sheets import sheets

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_sheets_connection():
    """Тестирование подключения к Google Sheets"""
    try:
        logger.info("🧪 Starting Google Sheets connection test...")
        
        # Подключение
        sheets.connect()
        
        logger.info("✅ Connection successful!")
        
        # Тест проверки email
        test_email = "test@example.com"
        logger.info(f"Testing email check with: {test_email}")
        exists = sheets.check_email_exists(test_email)
        logger.info(f"Email exists: {exists}")
        
        # Тест получения промокода
        logger.info("Testing promo code retrieval...")
        promo = sheets.get_available_promo()
        logger.info(f"Got promo code: {promo}")
        
        logger.info("🎉 All tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    return True

if __name__ == "__main__":
    success = test_sheets_connection()
    exit(0 if success else 1)


