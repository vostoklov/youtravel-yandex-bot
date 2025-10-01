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
    
    async def get_stats(self) -> Dict[str, int]:
        """Получить статистику"""
        async with self.pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM users")
            completed = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE completed_at IS NOT NULL"
            )
            return {
                "total_users": total,
                "completed_registrations": completed,
                "conversion_rate": round(completed / total * 100, 2) if total > 0 else 0
            }

# Глобальный инстанс
db = Database()
