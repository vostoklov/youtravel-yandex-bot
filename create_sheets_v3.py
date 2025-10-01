#!/usr/bin/env python3
"""
Создание Google Sheets через Drive API v3
"""
from google.oauth2 import service_account
from googleapiclient.discovery import build
import random
import string
import json
import ssl
import httplib2

# Отключаем SSL верификацию для обхода корпоративных прокси
ssl._create_default_https_context = ssl._create_unverified_context

def generate_promo_code():
    """Генерирует промокод вида YT-B2B-XXXXX"""
    chars = string.ascii_uppercase + string.digits
    return f"YT-B2B-{''.join(random.choice(chars) for _ in range(6))}"

def create_sheets_v3():
    """Создаёт таблицы через Drive API v3 + Sheets API v4"""
    
    # Загружаем credentials
    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    
    credentials = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES)
    
    # Создаём HTTP клиент с отключённой SSL верификацией и авторизуем его
    from google_auth_httplib2 import AuthorizedHttp
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    authorized_http = AuthorizedHttp(credentials, http=http)
    
    # Создаём клиентов для Drive и Sheets
    drive_service = build('drive', 'v3', http=authorized_http)
    sheets_service = build('sheets', 'v4', http=authorized_http)
    
    print("🔐 Авторизация успешна!\n")
    
    # ========== 1. СОЗДАЁМ ТАБЛИЦУ С EMAIL'АМИ ==========
    print("📧 Создаю таблицу с email'ами...")
    
    # Создаём файл через Drive API
    email_file_metadata = {
        'name': 'YouTravel Emails Database',
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    email_file = drive_service.files().create(body=email_file_metadata, fields='id').execute()
    email_sheet_id = email_file.get('id')
    
    print(f"✓ Файл создан, ID: {email_sheet_id}")
    
    # Заполняем данные через Sheets API
    test_emails = [
        ['email', 'name'],  # Заголовки
        ['ivan@youtravel.me', 'Иван Востоков'],
        ['test1@example.com', 'Александр Петров'],
        ['test2@example.com', 'Мария Иванова'],
        ['test3@example.com', 'Дмитрий Сидоров'],
        ['test4@example.com', 'Елена Смирнова'],
        ['test5@example.com', 'Андрей Козлов'],
        ['test6@example.com', 'Анна Морозова'],
        ['test7@example.com', 'Сергей Волков'],
        ['test8@example.com', 'Ольга Соколова'],
        ['test9@example.com', 'Павел Новиков']
    ]
    
    sheets_service.spreadsheets().values().update(
        spreadsheetId=email_sheet_id,
        range='Sheet1!A1:B11',
        valueInputOption='RAW',
        body={'values': test_emails}
    ).execute()
    
    print(f"✓ Данные загружены ({len(test_emails)-1} записей)")
    
    # Делаем публичным для чтения
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    drive_service.permissions().create(
        fileId=email_sheet_id,
        body=permission
    ).execute()
    
    print(f"✓ Доступ настроен (публичный на чтение)")
    print(f"✅ URL: https://docs.google.com/spreadsheets/d/{email_sheet_id}/edit\n")
    
    # ========== 2. СОЗДАЁМ ТАБЛИЦУ С ПРОМОКОДАМИ ==========
    print("🎟️  Создаю таблицу с промокодами...")
    
    # Создаём файл
    promo_file_metadata = {
        'name': 'YouTravel Promo Codes',
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    promo_file = drive_service.files().create(body=promo_file_metadata, fields='id').execute()
    promo_sheet_id = promo_file.get('id')
    
    print(f"✓ Файл создан, ID: {promo_sheet_id}")
    
    # Генерируем промокоды
    promo_data = [['promo_code', 'is_used']]  # Заголовки
    promo_data.extend([[generate_promo_code(), 'FALSE'] for _ in range(150)])
    
    # Загружаем всё одним батчем (Sheets API v4 поддерживает большие запросы)
    sheets_service.spreadsheets().values().update(
        spreadsheetId=promo_sheet_id,
        range='Sheet1!A1:B151',
        valueInputOption='RAW',
        body={'values': promo_data}
    ).execute()
    
    print(f"✓ Данные загружены (150 промокодов)")
    
    # Делаем публичным
    drive_service.permissions().create(
        fileId=promo_sheet_id,
        body=permission
    ).execute()
    
    print(f"✓ Доступ настроен (публичный на чтение)")
    print(f"✅ URL: https://docs.google.com/spreadsheets/d/{promo_sheet_id}/edit\n")
    
    # ========== ИТОГОВЫЙ ВЫВОД ==========
    print("=" * 70)
    print("🎉 ВСЁ ГОТОВО! Добавь эти ID в .env файл:")
    print("=" * 70)
    print(f"\nGOOGLE_SHEET_EMAILS_ID={email_sheet_id}")
    print(f"GOOGLE_SHEET_PROMOS_ID={promo_sheet_id}")
    print("\n📊 Полные URL для проверки:")
    print(f"Emails: https://docs.google.com/spreadsheets/d/{email_sheet_id}/edit")
    print(f"Promos: https://docs.google.com/spreadsheets/d/{promo_sheet_id}/edit")
    print("\n💡 Service Account для доступа:")
    print("claude-by-ivan-bortnikov@probable-bebop-305708.iam.gserviceaccount.com")
    print("=" * 70)
    
    return email_sheet_id, promo_sheet_id

if __name__ == '__main__':
    try:
        create_sheets_v3()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
