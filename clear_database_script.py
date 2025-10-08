#!/usr/bin/env python3
"""
Скрипт для очистки базы данных
Запускать через Railway CLI: railway run python clear_database_script.py
"""
import asyncio
import asyncpg
import os
from datetime import datetime

async def clear_database():
    try:
        print("🔗 Подключение к базе данных...")
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        
        print("📊 Получение статистики ДО очистки...")
        
        # Получаем статистику ДО очистки
        users_count = await conn.fetchval('SELECT COUNT(*) FROM users')
        reminders_count = await conn.fetchval('SELECT COUNT(*) FROM user_reminders')
        
        print(f"📊 ДО очистки:")
        print(f"   • Пользователей: {users_count}")
        print(f"   • Напоминаний: {reminders_count}")
        
        print("🗑️ Очистка базы данных...")
        
        # Очищаем таблицы
        await conn.execute('DELETE FROM user_reminders')
        await conn.execute('DELETE FROM users')
        
        print("✅ База данных очищена!")
        
        # Проверяем результат
        users_after = await conn.fetchval('SELECT COUNT(*) FROM users')
        reminders_after = await conn.fetchval('SELECT COUNT(*) FROM user_reminders')
        
        print(f"📊 ПОСЛЕ очистки:")
        print(f"   • Пользователей: {users_after}")
        print(f"   • Напоминаний: {reminders_after}")
        
        await conn.close()
        
        print(f"\n🎉 База данных готова к запуску рекламы!")
        print(f"⏰ Время очистки: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(clear_database())
