#!/usr/bin/env python3
"""
Скрипт для сброса регистрации пользователя в боте
"""
import asyncio
import logging
import sys
from database import db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def reset_user(telegram_id: int):
    """Удалить пользователя из базы для повторного тестирования"""
    try:
        await db.connect()
        
        # Проверяем существует ли пользователь
        user = await db.get_user(telegram_id)
        
        if not user:
            logger.warning(f"❌ User {telegram_id} not found in database")
            return False
        
        logger.info(f"Found user: {user}")
        logger.info(f"  Email: {user.get('email')}")
        logger.info(f"  INN: {user.get('inn')}")
        logger.info(f"  Promo: {user.get('promo_code')}")
        logger.info(f"  Completed: {user.get('completed_at')}")
        
        # Удаляем пользователя
        async with db.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM users WHERE telegram_id = $1",
                telegram_id
            )
            logger.info(f"✅ Deleted user {telegram_id} from database")
            logger.info(f"   SQL result: {result}")
        
        logger.info("🎉 User reset successful! You can now test /start again")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        await db.close()

async def list_users():
    """Показать всех пользователей в базе"""
    try:
        await db.connect()
        
        async with db.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM users ORDER BY created_at DESC")
            
            if not rows:
                logger.info("No users in database")
                return
            
            logger.info(f"Found {len(rows)} user(s):")
            logger.info("=" * 80)
            
            for row in rows:
                logger.info(f"Telegram ID: {row['telegram_id']}")
                logger.info(f"  Username: @{row['username']}")
                logger.info(f"  Email: {row['email']}")
                logger.info(f"  INN: {row['inn']}")
                logger.info(f"  Promo: {row['promo_code']}")
                logger.info(f"  Completed: {row['completed_at']}")
                logger.info(f"  Created: {row['created_at']}")
                logger.info("-" * 80)
        
    except Exception as e:
        logger.error(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        await db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  List all users:  python3 reset_user.py list")
        print("  Reset user:      python3 reset_user.py <telegram_id>")
        print()
        print("Example:")
        print("  python3 reset_user.py list")
        print("  python3 reset_user.py 123456789")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        asyncio.run(list_users())
    else:
        try:
            telegram_id = int(command)
            success = asyncio.run(reset_user(telegram_id))
            sys.exit(0 if success else 1)
        except ValueError:
            print(f"❌ Invalid telegram_id: {command}")
            print("Telegram ID must be a number")
            sys.exit(1)

