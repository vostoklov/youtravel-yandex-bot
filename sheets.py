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
            logger.info("=" * 60)
            logger.info("Starting Google Sheets connection...")
            logger.info("=" * 60)
            
            # Шаг 1: Читаем JSON из переменной окружения или файла
            logger.info("Step 1: Reading GOOGLE_CREDENTIALS_JSON from environment")
            creds_json_or_path = os.getenv('GOOGLE_CREDENTIALS_JSON')
            
            if not creds_json_or_path:
                logger.error("❌ GOOGLE_CREDENTIALS_JSON environment variable is not set!")
                raise ValueError("GOOGLE_CREDENTIALS_JSON not set")
            
            logger.info(f"✓ Got credentials value, length: {len(creds_json_or_path)} characters")
            
            # Шаг 2: Определяем - это путь к файлу или сам JSON?
            logger.info("Step 2: Determining if it's a file path or JSON string")
            
            # Если значение короткое и не начинается с '{', возможно это путь к файлу
            if len(creds_json_or_path) < 500 and not creds_json_or_path.strip().startswith('{'):
                # Вероятно, это путь к файлу
                logger.info(f"  Looks like a file path: {creds_json_or_path}")
                
                if not os.path.exists(creds_json_or_path):
                    logger.error(f"❌ Credentials file not found: {creds_json_or_path}")
                    raise FileNotFoundError(f"Credentials file not found: {creds_json_or_path}")
                
                logger.info(f"  Reading credentials from file: {creds_json_or_path}")
                with open(creds_json_or_path, 'r') as f:
                    creds_json = f.read()
                logger.info(f"✓ File read successfully, length: {len(creds_json)} characters")
            else:
                # Это сам JSON
                logger.info("  Detected as JSON string")
                creds_json = creds_json_or_path
                logger.info(f"  First 50 chars: {creds_json[:50]}...")
                logger.info(f"  Last 50 chars: ...{creds_json[-50:]}")
            
            # Шаг 3: Парсим JSON
            logger.info("Step 3: Parsing JSON credentials")
            try:
                creds_dict = json.loads(creds_json)
                logger.info("✓ JSON parsed successfully")
            except json.JSONDecodeError as je:
                logger.error(f"❌ JSON parsing failed at position {je.pos}")
                logger.error(f"   Error: {je.msg}")
                logger.error(f"   Context: ...{creds_json[max(0, je.pos-50):je.pos+50]}...")
                raise
            
            # Шаг 4: Проверяем наличие обязательных полей
            logger.info("Step 4: Validating credentials structure")
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in creds_dict]
            
            if missing_fields:
                logger.error(f"❌ Missing required fields: {missing_fields}")
                logger.error(f"   Available fields: {list(creds_dict.keys())}")
                raise ValueError(f"Missing required credential fields: {missing_fields}")
            
            logger.info(f"✓ All required fields present")
            logger.info(f"  Service account email: {creds_dict.get('client_email')}")
            logger.info(f"  Project ID: {creds_dict.get('project_id')}")
            
            # Шаг 5: Создаем credentials
            logger.info("Step 5: Creating ServiceAccountCredentials")
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            try:
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                logger.info("✓ Service account credentials created")
            except Exception as cred_error:
                logger.error(f"❌ Failed to create credentials: {type(cred_error).__name__}: {cred_error}")
                raise
            
            # Шаг 6: Авторизуем клиент
            logger.info("Step 6: Authorizing gspread client")
            try:
                self.client = gspread.authorize(creds)
                logger.info("✓ Gspread client authorized")
            except Exception as auth_error:
                logger.error(f"❌ Authorization failed: {type(auth_error).__name__}: {auth_error}")
                raise
            
            # Шаг 7: Открываем таблицу с email
            logger.info(f"Step 7: Opening spreadsheet with ID: {config.GOOGLE_SHEET_EMAILS_ID}")
            try:
                spreadsheet = self.client.open_by_key(config.GOOGLE_SHEET_EMAILS_ID)
                logger.info(f"✓ Spreadsheet opened: {spreadsheet.title}")
            except Exception as sheet_error:
                logger.error(f"❌ Failed to open spreadsheet: {type(sheet_error).__name__}: {sheet_error}")
                logger.error(f"   Make sure the service account {creds_dict.get('client_email')} has access to the sheet")
                raise
            
            # Шаг 8: Получаем первый worksheet
            logger.info("Step 8: Getting first worksheet")
            try:
                self.worksheet = spreadsheet.sheet1
                logger.info(f"✓ Worksheet loaded: {self.worksheet.title}")
            except Exception as ws_error:
                logger.error(f"❌ Failed to get worksheet: {type(ws_error).__name__}: {ws_error}")
                raise
            
            logger.info("=" * 60)
            logger.info("✅ Successfully connected to Google Sheets!")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ FAILED to connect to Google Sheets")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.error(f"   Error message: {str(e)}")
            logger.error("=" * 60)
            import traceback
            logger.error("Full traceback:")
            logger.error(traceback.format_exc())
            logger.error("=" * 60)
            raise
    
    def check_email_exists(self, email: str) -> bool:
        """Проверка существования email в базе верифицированных ТЭ"""
        try:
            # Убеждаемся, что подключение установлено
            if not self.client:
                self.connect()
            
            # Проверяем только в базе верифицированных ТЭ
            try:
                te_worksheet = self.client.open_by_key(config.GOOGLE_SHEET_EMAILS_ID).worksheet('Verified TE')
                
                # Получаем все email из столбца A (пропускаем заголовок)
                te_emails = te_worksheet.col_values(1)[1:]
                
                if email.lower() in [e.lower() for e in te_emails if e]:
                    logger.info(f"Email {email} found in verified TE database")
                    return True
                else:
                    logger.info(f"Email {email} not found in verified TE database")
                    return False
                            
            except Exception as te_error:
                logger.error(f"Could not check TE database: {te_error}")
                return False
            
        except Exception as e:
            logger.error(f"Error checking email: {e}")
            return False
    
    def get_available_promo(self) -> str:
        """Получить доступный промокод из таблицы промокодов"""
        try:
            logger.info("Getting available promo code from promos sheet...")
            
            # Убеждаемся, что подключение установлено
            if not self.client:
                self.connect()
            
            # Открываем основную таблицу
            spreadsheet = self.client.open_by_key(config.GOOGLE_SHEET_EMAILS_ID)
            
            # Получаем лист с промокодами
            try:
                promo_worksheet = spreadsheet.worksheet('Promos')
            except gspread.WorksheetNotFound:
                logger.error("Promos sheet not found")
                return None
            
            logger.info(f"Opened promo sheet: {promo_worksheet.title}")
            
            # Получаем все данные (промокоды и статусы)
            all_data = promo_worksheet.get_all_values()
            
            # Ищем первый доступный промокод (статус "available" или пустой)
            for i, row in enumerate(all_data[1:], 2):  # Пропускаем заголовок
                if len(row) >= 2:
                    promo_code = row[0].strip()
                    status = row[1].strip().lower() if len(row) > 1 else ""
                    
                    # Если промокод не пустой и статус "available" или пустой
                    if promo_code and (status == "available" or status == ""):
                        # Отмечаем промокод как использованный
                        promo_worksheet.update_cell(i, 2, "used")
                        
                        # Записываем реальную дату выдачи
                        from datetime import datetime
                        current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
                        promo_worksheet.update_cell(i, 3, current_date)
                        
                        logger.info(f"Returning promo code: {promo_code}")
                        return promo_code
            
            logger.warning("No available promo codes found!")
            return None
            
        except Exception as e:
            logger.error(f"Error getting promo code: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def get_available_promo_codes(self) -> list:
        """Получить все доступные промокоды"""
        try:
            # Убеждаемся, что подключение установлено
            if not self.client:
                self.connect()
            
            # Открываем основную таблицу
            spreadsheet = self.client.open_by_key(config.GOOGLE_SHEET_EMAILS_ID)
            
            # Получаем лист с промокодами
            try:
                promo_worksheet = spreadsheet.worksheet('Promos')
            except gspread.WorksheetNotFound:
                logger.error("Promos sheet not found")
                return []
            
            # Получаем все данные
            all_data = promo_worksheet.get_all_values()
            
            # Фильтруем только доступные промокоды
            available_promos = []
            for row in all_data[1:]:  # Пропускаем заголовок
                if len(row) >= 2:
                    promo_code = row[0].strip()
                    status = row[1].strip().lower() if len(row) > 1 else ""
                    
                    # Если промокод не пустой и статус "available" или пустой
                    if promo_code and (status == "available" or status == ""):
                        available_promos.append(promo_code)
            
            return available_promos
            
        except Exception as e:
            logger.error(f"Error getting promo codes: {type(e).__name__}: {e}")
            return []
    
    def check_email_already_registered(self, email: str) -> bool:
        """Проверить, не зарегистрирован ли уже этот email"""
        try:
            # Убеждаемся, что подключение установлено
            if not self.client:
                self.connect()
            
            # Открываем основную таблицу
            spreadsheet = self.client.open_by_key(config.GOOGLE_SHEET_EMAILS_ID)
            
            # Получаем лист с зарегистрированными пользователями
            try:
                registered_worksheet = spreadsheet.worksheet('Registered Users')
            except gspread.WorksheetNotFound:
                # Если листа нет, значит никто еще не регистрировался
                logger.info("Registered Users sheet not found - no registrations yet")
                return False
            
            # Получаем все email из столбца A (пропускаем заголовок)
            registered_emails = registered_worksheet.col_values(1)[1:]
            
            # Фильтруем пустые значения и проверяем, есть ли этот email в списке
            email_exists = email.lower() in [e.lower() for e in registered_emails if e and e.strip()]
            
            if email_exists:
                logger.info(f"Email {email} already registered")
            else:
                logger.info(f"Email {email} not registered yet")
                
            return email_exists
            
        except Exception as e:
            logger.error(f"Error checking email registration: {type(e).__name__}: {e}")
            return False
    
    def save_registration(self, email: str, inn: str, promo_code: str) -> bool:
        """Сохранить данные регистрации в Google Sheets"""
        try:
            # Убеждаемся, что подключение установлено
            if not self.client:
                self.connect()
            
            # Открываем основную таблицу
            spreadsheet = self.client.open_by_key(config.GOOGLE_SHEET_EMAILS_ID)
            
            # Получаем или создаем лист с зарегистрированными пользователями
            try:
                registered_worksheet = spreadsheet.worksheet('Registered Users')
            except gspread.WorksheetNotFound:
                # Создаем новый лист
                registered_worksheet = spreadsheet.add_worksheet(title='Registered Users', rows=1000, cols=5)
                
                # Добавляем заголовки
                headers = ['Email', 'ИНН', 'Промокод', 'Дата регистрации', 'Telegram ID']
                registered_worksheet.update('A1:E1', [headers])
                logger.info("Created Registered Users sheet with headers")
            
            # Добавляем новую запись
            from datetime import datetime
            current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
            
            # Получаем следующую свободную строку
            next_row = len(registered_worksheet.get_all_values()) + 1
            
            # Добавляем данные
            new_row = [email, inn, promo_code, current_date, '']  # Telegram ID оставляем пустым пока
            registered_worksheet.update(f'A{next_row}:E{next_row}', [new_row])
            
            logger.info(f"Saved registration: {email} -> {promo_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving registration: {type(e).__name__}: {e}")
            return False
    
    def remove_registration(self, email: str) -> bool:
        """Удалить запись регистрации из Google Sheets"""
        try:
            # Убеждаемся, что подключение установлено
            if not self.client:
                self.connect()
            
            # Открываем основную таблицу
            spreadsheet = self.client.open_by_key(config.GOOGLE_SHEET_EMAILS_ID)
            
            # Получаем лист с зарегистрированными пользователями
            try:
                registered_worksheet = spreadsheet.worksheet('Registered Users')
            except gspread.WorksheetNotFound:
                logger.info("Registered Users sheet not found - nothing to remove")
                return True
            
            # Получаем все данные
            all_data = registered_worksheet.get_all_values()
            
            # Ищем строку с нужным email
            for i, row in enumerate(all_data[1:], 2):  # Пропускаем заголовок
                if len(row) >= 1 and row[0].strip().lower() == email.lower():
                    # Удаляем строку (заменяем на пустые значения)
                    empty_row = ['', '', '', '', '']
                    registered_worksheet.update(f'A{i}:E{i}', [empty_row])
                    logger.info(f"Removed registration for email: {email}")
                    return True
            
            logger.info(f"Email {email} not found in registered users")
            return True
            
        except Exception as e:
            logger.error(f"Error removing registration: {type(e).__name__}: {e}")
            return False


# Глобальный экземпляр
sheets = SheetsManager()
