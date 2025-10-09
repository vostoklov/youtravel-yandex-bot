#!/usr/bin/env python3
"""
Исправление дубликатов для пользователя nzamaldinova@gmail.com
ВНИМАНИЕ: Этот скрипт удалит все записи кроме первой!
"""
import os
import sys
import asyncio
import asyncpg
import config

async def fix_duplicates():
    """Удаляем дубликаты, оставляем только первую запись"""
    try:
        pool = await asyncpg.create_pool(
            dsn=config.DATABASE_URL,
            min_size=1,
            max_size=3
        )
        
        async with pool.acquire() as conn:
            print("\n" + "="*60)
            print("🔧 ИСПРАВЛЕНИЕ ДУБЛИКАТОВ")
            print("="*60)
            
            # 1. Проверяем текущее состояние
            print("\n1️⃣ ТЕКУЩИЕ ЗАПИСИ:")
            current_records = await conn.fetch(
                """SELECT user_id, email, inn, promo_code, 
                          created_at, completed_at, step
                   FROM users 
                   WHERE email = 'nzamaldinova@gmail.com'
                   ORDER BY created_at"""
            )
            
            if not current_records:
                print("   ❌ Записей не найдено")
                await pool.close()
                return
            
            print(f"   Найдено записей: {len(current_records)}\n")
            for i, record in enumerate(current_records, 1):
                print(f"   Запись #{i}:")
                print(f"   👤 User ID: {record['user_id']}")
                print(f"   🎟️ Promo: {record['promo_code']}")
                print(f"   🏢 INN: {record['inn']}")
                print(f"   📍 Step: {record['step']}")
                print(f"   📅 Created: {record['created_at']}")
                print()
            
            if len(current_records) <= 1:
                print("   ✅ Дубликатов нет, исправление не требуется")
                await pool.close()
                return
            
            # 2. Определяем запись для сохранения
            # Оставляем запись с самой ранней датой создания и с ИНН
            keep_record = None
            for record in current_records:
                if record['inn']:  # Есть ИНН
                    keep_record = record
                    break
            
            if not keep_record:
                keep_record = current_records[0]  # Берем первую
            
            print(f"2️⃣ ЗАПИСЬ ДЛЯ СОХРАНЕНИЯ:")
            print(f"   👤 User ID: {keep_record['user_id']}")
            print(f"   🎟️ Promo: {keep_record['promo_code']}")
            print(f"   🏢 INN: {keep_record['inn']}")
            print(f"   📅 Created: {keep_record['created_at']}")
            
            # 3. Записи для удаления
            delete_records = [r for r in current_records if r['user_id'] != keep_record['user_id']]
            
            if not delete_records:
                print("\n   ✅ Нет записей для удаления")
                await pool.close()
                return
            
            print(f"\n3️⃣ ЗАПИСИ ДЛЯ УДАЛЕНИЯ ({len(delete_records)}):")
            promos_to_restore = []
            for record in delete_records:
                print(f"   ❌ User ID: {record['user_id']}, Promo: {record['promo_code']}")
                if record['promo_code'] and record['promo_code'] != keep_record['promo_code']:
                    promos_to_restore.append(record['promo_code'])
            
            # 4. Подтверждение
            print(f"\n⚠️ ВНИМАНИЕ!")
            print(f"   Будет удалено {len(delete_records)} записей")
            print(f"   Будет сохранена 1 запись (User ID: {keep_record['user_id']})")
            print(f"\n❓ Продолжить? (yes/no): ", end="")
            
            # В Railway CLI нет интерактивного ввода, поэтому просто выполняем
            # Для локального запуска раскомментируйте:
            # response = input()
            # if response.lower() != 'yes':
            #     print("   ❌ Отменено пользователем")
            #     await pool.close()
            #     return
            
            print("yes (автоматически)")
            
            # 5. Удаляем дубликаты
            print(f"\n4️⃣ УДАЛЕНИЕ ДУБЛИКАТОВ...")
            for record in delete_records:
                await conn.execute(
                    'DELETE FROM users WHERE user_id = $1',
                    record['user_id']
                )
                print(f"   ✅ Удален User ID: {record['user_id']}")
            
            # 6. Проверяем результат
            print(f"\n5️⃣ ПРОВЕРКА:")
            remaining = await conn.fetch(
                """SELECT user_id, promo_code 
                   FROM users 
                   WHERE email = 'nzamaldinova@gmail.com'"""
            )
            
            print(f"   Осталось записей: {len(remaining)}")
            for record in remaining:
                print(f"   ✅ User ID: {record['user_id']}, Promo: {record['promo_code']}")
            
            # 7. Промокоды для восстановления в Google Sheets
            print(f"\n6️⃣ ПРОМОКОДЫ ДЛЯ ВОССТАНОВЛЕНИЯ В GOOGLE SHEETS:")
            if promos_to_restore:
                for promo in promos_to_restore:
                    print(f"   🔄 {promo} → изменить статус на 'available'")
            else:
                print("   ℹ️ Нет промокодов для восстановления")
            
            print("\n" + "="*60)
            print("✅ ГОТОВО!")
            print("="*60)
        
        await pool.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(fix_duplicates())

