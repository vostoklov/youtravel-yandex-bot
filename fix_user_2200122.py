#!/usr/bin/env python3
"""
Исправление записи для пользователя 2200122
Устанавливаем правильный ИНН и промокод
"""
import asyncio
import asyncpg
import config

async def fix_user():
    """Исправляем данные пользователя"""
    try:
        pool = await asyncpg.create_pool(
            dsn=config.DATABASE_URL,
            min_size=1,
            max_size=3
        )
        
        async with pool.acquire() as conn:
            print("\n" + "="*60)
            print("🔧 ИСПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ 2200122")
            print("="*60)
            
            # Текущие данные
            current = await conn.fetchrow(
                'SELECT * FROM users WHERE user_id = $1',
                2200122
            )
            
            if not current:
                print("❌ Пользователь не найден!")
                await pool.close()
                return
            
            print("\n📊 ТЕКУЩИЕ ДАННЫЕ:")
            print(f"  Email: {current['email']}")
            print(f"  ИНН: {current['inn']}")
            print(f"  Промокод: {current['promo_code']}")
            print(f"  Этап: {current['step']}")
            
            # Обновляем данные
            print("\n🔄 ОБНОВЛЕНИЕ...")
            await conn.execute(
                """UPDATE users 
                   SET inn = $1, promo_code = $2
                   WHERE user_id = $3""",
                '7718718506',
                'YOUTRAVELGDLWN7IKDV',
                2200122
            )
            
            # Проверяем результат
            updated = await conn.fetchrow(
                'SELECT * FROM users WHERE user_id = $1',
                2200122
            )
            
            print("\n✅ ОБНОВЛЕННЫЕ ДАННЫЕ:")
            print(f"  Email: {updated['email']}")
            print(f"  ИНН: {updated['inn']}")
            print(f"  Промокод: {updated['promo_code']}")
            print(f"  Этап: {updated['step']}")
            
            print("\n" + "="*60)
            print("✅ ГОТОВО!")
            print("="*60)
        
        await pool.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_user())

