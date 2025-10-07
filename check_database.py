#!/usr/bin/env python3
"""
Скрипт для проверки базы данных PostgreSQL
"""
import asyncio
import asyncpg
import os
from datetime import datetime

async def check_database():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        
        print('🔍 Проверяем базу данных PostgreSQL:')
        print('=' * 50)
        
        # Получаем всех пользователей
        users = await conn.fetch('SELECT user_id, email, inn, promo_code, created_at FROM users ORDER BY created_at DESC')
        
        print(f'📊 Всего пользователей в базе: {len(users)}')
        
        if users:
            print(f'\n👥 Пользователи в базе данных:')
            print('-' * 80)
            for user in users:
                email = user['email'] or 'не указан'
                inn = user['inn'] or 'не указан'
                promo = user['promo_code'] or 'нет'
                date = user['created_at'].strftime('%d.%m %H:%M')
                print(f'ID: {user["user_id"]} | {email} | ИНН: {inn} | Промо: {promo} | {date}')
        
        # Проверяем конкретный ИНН
        target_inn = '5405021087'
        existing_inn = await conn.fetchval('SELECT inn FROM users WHERE inn = $1', target_inn)
        
        print(f'\n🔍 Проверка ИНН {target_inn}:')
        if existing_inn:
            print(f'❌ ИНН {target_inn} найден в базе данных!')
        else:
            print(f'✅ ИНН {target_inn} НЕ найден в базе данных')
        
        await conn.close()
        
    except Exception as e:
        print(f'❌ Ошибка: {e}')

if __name__ == "__main__":
    asyncio.run(check_database())
