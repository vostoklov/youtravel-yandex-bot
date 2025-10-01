#!/usr/bin/env python3
"""
Скрипт для создания Google Sheets таблиц для YouTravel бота
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import string

def generate_promo_code():
    """Генерирует промокод вида YT-B2B-XXXXX"""
    chars = string.ascii_uppercase + string.digits
    return f"YT-B2B-{''.join(random.choice(chars) for _ in range(6))}"

def create_sheets():
    """Создаёт две Google Sheets таблицы"""
    
    # Аутентификация
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    
    print("🔐 Авторизация успешна!")
    
    # 1. Создаём таблицу с email'ами
    print("\n📧 Создаю таблицу с email'ами YouTravel...")
    email_sheet = client.create('YouTravel Emails Database')
    email_worksheet = email_sheet.get_worksheet(0)
    
    # Заголовки
    email_worksheet.update('A1:B1', [['email', 'name']])
    
    # Тестовые данные (10 записей)
    test_emails = [
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
    
    email_worksheet.update('A2:B11', test_emails)
    email_sheet.share('', perm_type='anyone', role='reader')  # Публичный доступ на чтение
    
    print(f"✅ Таблица создана!")
    print(f"📊 URL: {email_sheet.url}")
    print(f"🔑 ID: {email_sheet.id}")
    
    # 2. Создаём таблицу с промокодами
    print("\n🎟️  Создаю таблицу с промокодами...")
    promo_sheet = client.create('YouTravel Promo Codes')
    promo_worksheet = promo_sheet.get_worksheet(0)
    
    # Заголовки
    promo_worksheet.update('A1:B1', [['promo_code', 'is_used']])
    
    # Генерируем 150 промокодов
    promo_codes = [[generate_promo_code(), 'FALSE'] for _ in range(150)]
    
    # Обновляем батчами (Google Sheets API ограничивает размер запроса)
    batch_size = 50
    for i in range(0, len(promo_codes), batch_size):
        batch = promo_codes[i:i+batch_size]
        start_row = i + 2  # +2 потому что строка 1 — заголовки, и индексация с 1
        end_row = start_row + len(batch) - 1
        promo_worksheet.update(f'A{start_row}:B{end_row}', batch)
        print(f"  ✓ Загружено {min(i+batch_size, len(promo_codes))}/{len(promo_codes)} промокодов...")
    
    promo_sheet.share('', perm_type='anyone', role='reader')  # Публичный доступ на чтение
    
    print(f"✅ Таблица создана!")
    print(f"📊 URL: {promo_sheet.url}")
    print(f"🔑 ID: {promo_sheet.id}")
    
    # Выводим итоговую информацию
    print("\n" + "="*70)
    print("🎉 ВСЁ ГОТОВО! Добавь эти ID в .env файл:")
    print("="*70)
    print(f"\nGOOGLE_SHEET_EMAILS_ID={email_sheet.id}")
    print(f"GOOGLE_SHEET_PROMOS_ID={promo_sheet.id}")
    print("\nПолные URL для проверки:")
    print(f"Emails: {email_sheet.url}")
    print(f"Promos: {promo_sheet.url}")
    print("\n💡 Service Account email для доступа:")
    print(f"claude@probable-bebop-305708.iam.gserviceaccount.com")
    print("="*70)

if __name__ == '__main__':
    try:
        create_sheets()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
