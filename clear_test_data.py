#!/usr/bin/env python3
"""
Скрипт для очистки тестовых данных перед запуском
"""
import asyncio
import asyncpg
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def clear_test_data():
    """Очистка тестовых данных"""
    try:
        # Подключаемся к базе
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        
        print("🧹 Начинаем очистку тестовых данных...")
        
        # Получаем статистику до очистки
        total_users = await conn.fetchval('SELECT COUNT(*) FROM users')
        completed_users = await conn.fetchval('SELECT COUNT(*) FROM users WHERE completed_at IS NOT NULL')
        
        print(f"📊 До очистки:")
        print(f"   • Всего пользователей: {total_users}")
        print(f"   • Завершили регистрацию: {completed_users}")
        
        # Получаем всех пользователей для просмотра
        users = await conn.fetch('''
            SELECT user_id, email, created_at, completed_at, promo_code 
            FROM users 
            ORDER BY created_at
        ''')
        
        print(f"\n👥 Пользователи в базе:")
        print("=" * 80)
        for user in users:
            status = '✅ Завершен' if user['completed_at'] else '⏳ В процессе'
            date = user['created_at'].strftime('%d.%m %H:%M')
            email = user['email'] or 'не указан'
            promo = user['promo_code'] or 'нет'
            print(f'ID: {user["user_id"]} | {email} | {status} | {date} | Промо: {promo}')
        
        # Спрашиваем подтверждение
        print(f"\n⚠️  ВНИМАНИЕ: Это удалит ВСЕХ пользователей из базы данных!")
        print("Это действие нельзя отменить!")
        
        confirm = input("\nПродолжить? (yes/no): ").lower().strip()
        if confirm != 'yes':
            print("❌ Операция отменена")
            await conn.close()
            return
        
        # Очищаем все таблицы
        print("\n🗑️  Удаляем пользователей...")
        await conn.execute('DELETE FROM users')
        
        print("🗑️  Удаляем напоминания...")
        await conn.execute('DELETE FROM user_reminders')
        
        # Получаем статистику после очистки
        total_users_after = await conn.fetchval('SELECT COUNT(*) FROM users')
        completed_users_after = await conn.fetchval('SELECT COUNT(*) FROM users WHERE completed_at IS NOT NULL')
        
        print(f"\n✅ Очистка завершена!")
        print(f"📊 После очистки:")
        print(f"   • Всего пользователей: {total_users_after}")
        print(f"   • Завершили регистрацию: {completed_users_after}")
        
        await conn.close()
        print("\n🎉 База данных очищена и готова к запуску!")
        
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(clear_test_data())
