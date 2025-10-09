#!/usr/bin/env python3
"""
Анализ проблемы с множественной выдачей промокодов
"""
import os
import sys
import asyncio
import asyncpg
import config
from datetime import datetime

async def analyze_issue():
    """Полный анализ проблемы"""
    try:
        pool = await asyncpg.create_pool(
            dsn=config.DATABASE_URL,
            min_size=1,
            max_size=3
        )
        
        async with pool.acquire() as conn:
            print("\n" + "="*60)
            print("📊 АНАЛИЗ ПРОБЛЕМЫ С ПРОМОКОДАМИ")
            print("="*60)
            
            # 1. Все пользователи с завершенной регистрацией
            print("\n1️⃣ ПОЛЬЗОВАТЕЛИ С ЗАВЕРШЕННОЙ РЕГИСТРАЦИЕЙ:")
            completed_users = await conn.fetch(
                """SELECT user_id, email, inn, promo_code, 
                          created_at, completed_at 
                   FROM users 
                   WHERE step = 'completed'
                   ORDER BY completed_at DESC"""
            )
            
            if completed_users:
                for user in completed_users:
                    print(f"\n👤 User ID: {user['user_id']}")
                    print(f"   📧 Email: {user['email']}")
                    print(f"   🏢 INN: {user['inn']}")
                    print(f"   🎟️ Promo: {user['promo_code']}")
                    print(f"   📅 Started: {user['created_at']}")
                    print(f"   ✅ Completed: {user['completed_at']}")
            else:
                print("   ❌ Нет пользователей с завершенной регистрацией")
            
            # 2. Все пользователи с email nzamaldinova@gmail.com
            print("\n2️⃣ ВСЕ ЗАПИСИ ДЛЯ nzamaldinova@gmail.com:")
            nz_users = await conn.fetch(
                """SELECT * FROM users 
                   WHERE email = 'nzamaldinova@gmail.com'
                   ORDER BY created_at"""
            )
            
            if nz_users:
                for i, user in enumerate(nz_users, 1):
                    print(f"\n   Запись #{i}:")
                    print(f"   👤 User ID: {user['user_id']}")
                    print(f"   📧 Email: {user['email']}")
                    print(f"   🏢 INN: {user['inn']}")
                    print(f"   🎟️ Promo: {user['promo_code']}")
                    print(f"   📍 Step: {user['step']}")
                    print(f"   📅 Created: {user['created_at']}")
                    print(f"   ✅ Completed: {user['completed_at']}")
            else:
                print("   ❌ Записей не найдено")
            
            # 3. Все пользователи с промокодами
            print("\n3️⃣ ВСЕ ПОЛЬЗОВАТЕЛИ С ПРОМОКОДАМИ:")
            users_with_promos = await conn.fetch(
                """SELECT user_id, email, promo_code, completed_at 
                   FROM users 
                   WHERE promo_code IS NOT NULL
                   ORDER BY completed_at DESC"""
            )
            
            promo_count = {}
            for user in users_with_promos:
                promo = user['promo_code']
                if promo in promo_count:
                    promo_count[promo] += 1
                else:
                    promo_count[promo] = 1
                print(f"   🎟️ {promo} → User {user['user_id']} ({user['email']})")
            
            # 4. Проверка дубликатов промокодов
            print("\n4️⃣ ДУБЛИКАТЫ ПРОМОКОДОВ В БД:")
            duplicates = [promo for promo, count in promo_count.items() if count > 1]
            if duplicates:
                for promo in duplicates:
                    print(f"   ⚠️ {promo} выдан {promo_count[promo]} раз(а)!")
            else:
                print("   ✅ Дубликатов не найдено")
            
            # 5. Статистика
            print("\n5️⃣ СТАТИСТИКА:")
            total_users = await conn.fetchval('SELECT COUNT(*) FROM users')
            completed = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE step = 'completed'"
            )
            with_promos = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE promo_code IS NOT NULL"
            )
            
            print(f"   • Всего пользователей: {total_users}")
            print(f"   • Завершили регистрацию: {completed}")
            print(f"   • Получили промокоды: {with_promos}")
            
            # 6. Рекомендации
            print("\n" + "="*60)
            print("💡 РЕКОМЕНДАЦИИ:")
            print("="*60)
            
            if len(nz_users) > 1:
                print(f"\n⚠️ Найдено {len(nz_users)} записей для nzamaldinova@gmail.com")
                print("   Рекомендация: Оставить только одну запись с первым промокодом")
                print("   Команда для очистки будет предоставлена отдельно")
            
            promos_to_restore = [
                'YOUTRAVELCME4IAZJU6',
                'YOUTRAVELOZ3DZVJ7NQ', 
                'YOUTRAVELJFUHCYBOZT',
                'YOUTRAVELBRGJJ77O22',
                'YOUTRAVELOB4VD2YBL7',
                'YOUTRAVELBVHEW48XL7',
                'YOUTRAVELPXP5N77LH7',
                'YOUTRAVELLBXZL6T3G3'
            ]
            
            print(f"\n📋 Промокоды для восстановления в Google Sheets:")
            for promo in promos_to_restore:
                print(f"   • {promo} → вернуть статус 'available'")
            
            print("\n" + "="*60)
        
        await pool.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(analyze_issue())

