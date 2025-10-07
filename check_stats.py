#!/usr/bin/env python3
"""
Скрипт для проверки статистики базы данных
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

async def check_stats():
    """Проверка статистики базы данных"""
    try:
        # Подключаемся к базе
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        
        print("📊 Статистика базы данных")
        print("=" * 50)
        
        # Общая статистика
        total_users = await conn.fetchval('SELECT COUNT(*) FROM users')
        completed_users = await conn.fetchval('SELECT COUNT(*) FROM users WHERE completed_at IS NOT NULL')
        incomplete_users = total_users - completed_users
        
        # Конверсия
        conversion = (completed_users / total_users * 100) if total_users > 0 else 0
        
        print(f"👥 Пользователи:")
        print(f"   • Всего: {total_users}")
        print(f"   • Завершили: {completed_users}")
        print(f"   • В процессе: {incomplete_users}")
        print(f"   • Конверсия: {conversion:.1f}%")
        
        # Статистика за последние 24 часа
        yesterday = datetime.now() - timedelta(days=1)
        new_users_24h = await conn.fetchval('''
            SELECT COUNT(*) FROM users WHERE created_at >= $1
        ''', yesterday)
        
        completed_24h = await conn.fetchval('''
            SELECT COUNT(*) FROM users WHERE completed_at >= $1
        ''', yesterday)
        
        print(f"\n📅 За последние 24 часа:")
        print(f"   • Новых пользователей: {new_users_24h}")
        print(f"   • Завершили: {completed_24h}")
        
        # Статистика промокодов
        promo_issued = await conn.fetchval('SELECT COUNT(*) FROM users WHERE promo_code IS NOT NULL')
        
        print(f"\n🎟️ Промокоды:")
        print(f"   • Выдано: {promo_issued}")
        
        # Детали пользователей
        users = await conn.fetch('''
            SELECT user_id, email, created_at, completed_at, promo_code 
            FROM users 
            ORDER BY created_at DESC
        ''')
        
        print(f"\n👥 Детали пользователей:")
        print("=" * 80)
        for user in users:
            status = '✅ Завершен' if user['completed_at'] else '⏳ В процессе'
            date = user['created_at'].strftime('%d.%m %H:%M')
            email = user['email'] or 'не указан'
            promo = user['promo_code'] or 'нет'
            print(f'ID: {user["user_id"]} | {email} | {status} | {date} | Промо: {promo}')
        
        # Статистика напоминаний
        total_reminders = await conn.fetchval('SELECT COUNT(*) FROM user_reminders')
        print(f"\n🔔 Напоминания:")
        print(f"   • Всего отправлено: {total_reminders}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при проверке статистики: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_stats())
