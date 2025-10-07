#!/usr/bin/env python3
"""
Скрипт для очистки базы данных перед запуском
"""
import asyncio
import asyncpg
import os
from datetime import datetime

async def clear_database():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        
        print('🗑️ Очистка базы данных PostgreSQL:')
        print('=' * 50)
        
        # Получаем статистику ДО очистки
        users_count = await conn.fetchval('SELECT COUNT(*) FROM users')
        reminders_count = await conn.fetchval('SELECT COUNT(*) FROM user_reminders')
        
        print(f'📊 Перед очисткой:')
        print(f'   • Пользователей: {users_count}')
        print(f'   • Напоминаний: {reminders_count}')
        
        # Очищаем таблицы
        await conn.execute('DELETE FROM user_reminders')
        await conn.execute('DELETE FROM users')
        
        print(f'\n✅ База данных очищена!')
        
        # Проверяем результат
        users_after = await conn.fetchval('SELECT COUNT(*) FROM users')
        reminders_after = await conn.fetchval('SELECT COUNT(*) FROM user_reminders')
        
        print(f'📊 После очистки:')
        print(f'   • Пользователей: {users_after}')
        print(f'   • Напоминаний: {reminders_after}')
        
        await conn.close()
        
        print(f'\n🎉 База данных готова к запуску!')
        
    except Exception as e:
        print(f'❌ Ошибка: {e}')

if __name__ == "__main__":
    asyncio.run(clear_database())
