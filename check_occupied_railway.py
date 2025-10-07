#!/usr/bin/env python3
"""
Скрипт для проверки занятых данных через Railway
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
        # Подключаемся к базе данных Railway
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
