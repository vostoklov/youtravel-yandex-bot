#!/usr/bin/env python3
"""
Скрипт для проверки занятых данных в системе
"""
import asyncio
import asyncpg
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def check_occupied_data():
    """Проверка занятых данных в системе"""
    try:
        # Подключаемся к базе данных
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        
        print("🔍 Анализ занятых данных в системе")
        print("=" * 60)
        
        # Получаем всех пользователей из базы данных
        users = await conn.fetch('''
            SELECT user_id, email, inn, promo_code, created_at, completed_at 
            FROM users 
            ORDER BY created_at DESC
        ''')
        
        print(f"📊 Всего пользователей в базе данных: {len(users)}")
        
        if users:
            print(f"\n👥 Пользователи в базе данных:")
            print("-" * 80)
            for user in users:
                status = '✅ Завершен' if user['completed_at'] else '⏳ В процессе'
                date = user['created_at'].strftime('%d.%m %H:%M')
                email = user['email'] or 'не указан'
                inn = user['inn'] or 'не указан'
                promo = user['promo_code'] or 'нет'
                print(f'ID: {user["user_id"]} | {email} | {status} | {date}')
                print(f'    ИНН: {inn} | Промо: {promo}')
                print()
        
        # Получаем данные из Google Sheets
        print("📋 Данные из Google Sheets:")
        print("-" * 80)
        
        # Импортируем sheets здесь, чтобы избежать проблем с async
        from sheets import sheets
        
        # Проверяем зарегистрированных пользователей в Google Sheets
        try:
            # Открываем лист с зарегистрированными пользователями
            import gspread
            from oauth2client.service_account import ServiceAccountCredentials
            import json
            
            # Читаем credentials
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', 'credentials.json')
            if os.path.exists(credentials_json):
                with open(credentials_json, 'r') as f:
                    creds_data = json.load(f)
            else:
                creds_data = json.loads(credentials_json)
            
            # Подключаемся
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_data, scope)
            client = gspread.authorize(creds)
            
            # Открываем таблицу
            spreadsheet = client.open_by_key(os.getenv('GOOGLE_SHEET_EMAILS_ID'))
            
            try:
                registered_worksheet = spreadsheet.worksheet('Registered Users')
                all_data = registered_worksheet.get_all_values()
                
                print(f"📊 Записей в Google Sheets: {len(all_data) - 1}")  # -1 для заголовка
                
                if len(all_data) > 1:
                    print(f"\n📋 Зарегистрированные пользователи:")
                    print("-" * 80)
                    for i, row in enumerate(all_data[1:], 2):
                        if len(row) >= 4 and row[0].strip():  # Если есть email
                            email = row[0]
                            inn = row[1] if len(row) > 1 else ''
                            promo = row[2] if len(row) > 2 else ''
                            date = row[3] if len(row) > 3 else ''
                            print(f'{i-1}. {email} | ИНН: {inn} | Промо: {promo} | {date}')
                else:
                    print("📝 Нет зарегистрированных пользователей в Google Sheets")
                    
            except gspread.WorksheetNotFound:
                print("📝 Лист 'Registered Users' не найден - нет зарегистрированных пользователей")
                
        except Exception as e:
            print(f"❌ Ошибка при работе с Google Sheets: {e}")
        
        # Анализ занятых данных
        print(f"\n🔒 Анализ занятых данных:")
        print("-" * 80)
        
        # Занятые email
        occupied_emails = []
        occupied_inns = []
        occupied_promos = []
        
        for user in users:
            if user['email']:
                occupied_emails.append(user['email'])
            if user['inn']:
                occupied_inns.append(user['inn'])
            if user['promo_code']:
                occupied_promos.append(user['promo_code'])
        
        print(f"📧 Занятые email ({len(occupied_emails)}):")
        for email in occupied_emails:
            print(f"   • {email}")
        
        print(f"\n🏢 Занятые ИНН ({len(occupied_inns)}):")
        for inn in occupied_inns:
            print(f"   • {inn}")
        
        print(f"\n🎟️ Занятые промокоды ({len(occupied_promos)}):")
        for promo in occupied_promos:
            print(f"   • {promo}")
        
        await conn.close()
        
        print(f"\n✅ Анализ завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка при анализе данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_occupied_data())
