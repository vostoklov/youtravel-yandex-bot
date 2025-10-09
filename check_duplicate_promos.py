#!/usr/bin/env python3
"""
Проверка дубликатов промокодов для пользователя 2200122
"""
import os
import sys
import asyncio
import asyncpg
from config import Config

async def check_user_promos():
    """Проверяем промокоды пользователя"""
    config = Config()
    
    try:
        pool = await asyncpg.create_pool(
            dsn=config.DATABASE_URL,
            min_size=1,
            max_size=3
        )
        
        async with pool.acquire() as conn:
            # Проверяем пользователя 2200122
            user = await conn.fetchrow(
                'SELECT * FROM users WHERE user_id = $1',
                2200122
            )
            
            if user:
                print(f"\n📊 Данные пользователя 2200122:")
                print(f"Email: {user['email']}")
                print(f"INN: {user['inn']}")
                print(f"Promo: {user['promo_code']}")
                print(f"Step: {user['step']}")
                print(f"Created: {user['created_at']}")
                print(f"Completed: {user['completed_at']}")
            else:
                print("❌ Пользователь не найден")
        
        await pool.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(check_user_promos())

