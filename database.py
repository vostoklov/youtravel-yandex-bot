"""
Работа с PostgreSQL базой данных
"""
import asyncpg
from typing import Optional, Dict, Any
import config
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Создаёт connection pool"""
        self.pool = await asyncpg.create_pool(
            config.DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        logger.info("✅ Connected to database")
        await self.create_tables()
    
    async def close(self):
        """Закрывает connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection closed")
    
    async def create_tables(self):
        """Создаёт таблицы если их нет"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    telegram_username TEXT,
                    email TEXT,
                    inn TEXT,
                    promo_code TEXT,
                    step TEXT DEFAULT 'start',
                    created_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP,
                    UNIQUE(inn)
                )
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_inn ON users(inn)
            """)
            
            logger.info("✅ Tables created/verified")
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить пользователя по ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE user_id = $1",
                user_id
            )
            return dict(row) if row else None
    
    async def create_user(self, user_id: int, username: Optional[str] = None):
        """Создать нового пользователя"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (user_id, telegram_username, step)
                VALUES ($1, $2, 'email')
                ON CONFLICT (user_id) DO NOTHING
            """, user_id, username)
            logger.info(f"User {user_id} created")
    
    async def update_user(self, user_id: int, **kwargs):
        """Обновить данные пользователя"""
        if not kwargs:
            return
        
        set_clause = ", ".join([f"{k} = ${i+2}" for i, k in enumerate(kwargs.keys())])
        values = [user_id] + list(kwargs.values())
        
        async with self.pool.acquire() as conn:
            await conn.execute(
                f"UPDATE users SET {set_clause} WHERE user_id = $1",
                *values
            )
            logger.info(f"User {user_id} updated: {kwargs}")
    
    async def check_inn_exists(self, inn: str) -> bool:
        """Проверить существует ли уже такой ИНН"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM users WHERE inn = $1)",
                inn
            )
            return result
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получить базовую статистику"""
        async with self.pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM users")
            completed = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE completed_at IS NOT NULL"
            )
            promo_codes_issued = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE promo_code IS NOT NULL"
            )
            return {
                "total_users": total,
                "completed_users": completed,
                "conversion_rate": round(completed / total * 100, 2) if total > 0 else 0,
                "promo_codes_issued": promo_codes_issued
            }
    
    async def get_detailed_stats(self) -> Dict[str, Any]:
        """Получить детальную статистику"""
        async with self.pool.acquire() as conn:
            # Общая статистика
            total = await conn.fetchval("SELECT COUNT(*) FROM users")
            completed = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE completed_at IS NOT NULL"
            )
            in_progress = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE completed_at IS NULL AND step != 'start'"
            )
            
            # За последние 24 часа
            users_last_24h = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE created_at > NOW() - INTERVAL '24 hours'"
            )
            completed_last_24h = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE completed_at > NOW() - INTERVAL '24 hours'"
            )
            
            # Промокоды
            promo_codes_issued = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE promo_code IS NOT NULL"
            )
            
            return {
                "total_users": total,
                "completed_users": completed,
                "in_progress_users": in_progress,
                "conversion_rate": round(completed / total * 100, 2) if total > 0 else 0,
                "users_last_24h": users_last_24h,
                "completed_last_24h": completed_last_24h,
                "promo_codes_issued": promo_codes_issued,
                "available_promos": 0  # Будет заполнено из sheets
            }
    
    async def get_recent_users(self, limit: int = 10) -> list:
        """Получить последних пользователей"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM users ORDER BY created_at DESC LIMIT $1",
                limit
            )
            return [dict(row) for row in rows]
    
    async def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM users WHERE user_id = $1",
                user_id
            )
            return result == "DELETE 1"

# Глобальный инстанс
db = Database()
