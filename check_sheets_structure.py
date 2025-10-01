#!/usr/bin/env python3
"""
Скрипт для проверки структуры Google Sheets таблиц
"""
import logging
from sheets import sheets
import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_sheets_structure():
    """Проверка структуры обеих таблиц"""
    try:
        # Подключение
        sheets.connect()
        
        # Проверка таблицы Emails
        logger.info("=" * 80)
        logger.info("📧 Checking EMAILS table structure")
        logger.info("=" * 80)
        
        # Первые 5 строк из колонки A
        emails_col_a = sheets.worksheet.col_values(1)[:5]
        logger.info(f"Column A (first 5 rows): {emails_col_a}")
        
        # Проверяем есть ли другие колонки
        try:
            emails_col_b = sheets.worksheet.col_values(2)[:5]
            logger.info(f"Column B (first 5 rows): {emails_col_b}")
        except:
            logger.info("Column B: empty or doesn't exist")
        
        # Проверка таблицы Promos
        logger.info("")
        logger.info("=" * 80)
        logger.info("🎟️  Checking PROMOS table structure")
        logger.info("=" * 80)
        
        # Открываем таблицу с промокодами
        promo_sheet = sheets.client.open_by_key(config.GOOGLE_SHEET_PROMOS_ID)
        promo_worksheet = promo_sheet.sheet1
        
        logger.info(f"Promo sheet title: {promo_sheet.title}")
        logger.info(f"Worksheet title: {promo_worksheet.title}")
        
        # Первые 5 строк из всех колонок
        all_values = promo_worksheet.get_all_values()[:5]
        logger.info(f"First 5 rows (all columns):")
        for i, row in enumerate(all_values, 1):
            logger.info(f"  Row {i}: {row}")
        
        # Колонка A
        promo_col_a = promo_worksheet.col_values(1)[:5]
        logger.info(f"\nColumn A (first 5 rows): {promo_col_a}")
        
        # Колонка B
        try:
            promo_col_b = promo_worksheet.col_values(2)[:5]
            logger.info(f"Column B (first 5 rows): {promo_col_b}")
        except:
            logger.info("Column B: empty or doesn't exist")
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("💡 Recommendations:")
        logger.info("=" * 80)
        logger.info("Emails table should have:")
        logger.info("  Column A: email addresses (e.g., user@youtravel.me)")
        logger.info("")
        logger.info("Promos table should have:")
        logger.info("  Column A: Header (e.g., 'Promo Code')")
        logger.info("  Column B: Actual promo codes (e.g., YANDEX10OFF1, YANDEX10OFF2...)")
        logger.info("  OR")
        logger.info("  Column A: Promo codes directly (if no header)")
        logger.info("")
        logger.info("Current code expects promos in Column B (index 2)")
        logger.info("If your promos are in Column A, change code: col_values(2) → col_values(1)")
        
    except Exception as e:
        logger.error(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    return True

if __name__ == "__main__":
    success = check_sheets_structure()
    exit(0 if success else 1)

