"""
Система автонапоминаний для пользователей
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import config
from database import db

logger = logging.getLogger(__name__)

class ReminderSystem:
    def __init__(self):
        self.bot = None
        self.reminder_intervals = {
            'incomplete_1h': 60,      # 1 час после начала
            'incomplete_24h': 1440,   # 24 часа
            'incomplete_3d': 4320,    # 3 дня
            'promo_reminder': 10080,  # 7 дней после получения промокода
        }
    
    async def start_reminders(self, bot):
        """Запуск системы напоминаний"""
        self.bot = bot
        logger.info("🔔 Starting reminder system...")
        
        while True:
            try:
                await self.check_incomplete_registrations()
                await self.check_promo_reminders()
                await asyncio.sleep(300)  # Проверяем каждые 5 минут
                
            except Exception as e:
                logger.error(f"Reminder system error: {e}")
                await asyncio.sleep(60)  # 1 минута при ошибке
    
    async def check_incomplete_registrations(self):
        """Проверка незавершенных регистраций"""
        try:
            # Получаем пользователей с незавершенной регистрацией
            incomplete_users = await self.get_incomplete_users()
            
            for user in incomplete_users:
                await self.send_reminder_if_needed(user)
                
        except Exception as e:
            logger.error(f"Error checking incomplete registrations: {e}")
    
    async def get_incomplete_users(self) -> List[Dict[str, Any]]:
        """Получаем пользователей с незавершенной регистрацией"""
        try:
            async with db.pool.acquire() as conn:
                # Пользователи без completed_at
                rows = await conn.fetch("""
                    SELECT user_id, email, step, created_at, completed_at
                    FROM users 
                    WHERE completed_at IS NULL
                    ORDER BY created_at DESC
                """)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting incomplete users: {e}")
            return []
    
    async def send_reminder_if_needed(self, user: Dict[str, Any]):
        """Отправляем напоминание если нужно"""
        try:
            user_id = user['user_id']
            created_at = user['created_at']
            step = user['step']
            
            # Вычисляем время с момента создания
            time_since_creation = datetime.now() - created_at
            minutes_since = int(time_since_creation.total_seconds() / 60)
            
            # Определяем тип напоминания (отправляем самое подходящее)
            reminder_type = None
            if minutes_since >= self.reminder_intervals['incomplete_3d']:
                reminder_type = 'incomplete_3d'
            elif minutes_since >= self.reminder_intervals['incomplete_24h']:
                reminder_type = 'incomplete_24h'
            elif minutes_since >= self.reminder_intervals['incomplete_1h']:
                reminder_type = 'incomplete_1h'
            
            if reminder_type:
                await self.send_reminder(user_id, reminder_type, step)
                
        except Exception as e:
            logger.error(f"Error sending reminder to user {user.get('user_id')}: {e}")
    
    async def send_reminder(self, user_id: int, reminder_type: str, step: str):
        """Отправляем конкретное напоминание"""
        try:
            # Проверяем, не отправляли ли уже это напоминание
            if await self.reminder_already_sent(user_id, reminder_type):
                return
            
            message = self.get_reminder_message(reminder_type, step)
            
            if message:
                await self.bot.send_message(user_id, message, parse_mode="HTML")
                await self.mark_reminder_sent(user_id, reminder_type)
                logger.info(f"Reminder {reminder_type} sent to user {user_id}")
                
        except Exception as e:
            if "chat not found" in str(e) or "bot was blocked" in str(e):
                logger.warning(f"User {user_id} blocked the bot or chat not found - skipping reminder")
                # Отмечаем напоминание как отправленное, чтобы не спамить
                await self.mark_reminder_sent(user_id, reminder_type)
            else:
                logger.error(f"Error sending reminder to user {user_id}: {e}")
    
    def get_reminder_message(self, reminder_type: str, step: str) -> str:
        """Получаем текст напоминания"""
        messages = {
            'incomplete_1h': {
                'email': """
⏰ <b>Напоминание</b>

Вы начали оформление участия в партнёрстве YouTravel × Яндекс.Путешествия, но не закончили.

💡 Завершите, чтобы получить промокод −10% на бронирования отелей для ваших туров.

👉 Нажмите /start и продолжите прямо сейчас.
                """,
                'inn': """
⏰ <b>Напоминание</b>

Вы зарегистрировались в Яндекс.Путешествиях, но не ввели ИНН вашей компании.

💼 Укажите ИНН, чтобы активировать персональную скидку −10% на отели.

👉 Нажмите /start и продолжите прямо сейчас.
                """,
                'confirmation': """
⏰ <b>Напоминание</b>

Вы ввели все данные, но не подтвердили участие в партнёрстве.

✅ Подтвердите, чтобы получить промокод −10% на бронирования отелей.

👉 Нажмите /start и завершите сейчас.
                """
            },
            'incomplete_24h': {
                'email': """
🔄 <b>Почти готово!</b>

Остался один шаг до получения вашего промокода −10% на отели Яндекс.Путешествий.

📧 Укажите email от YouTravel, чтобы активировать персональную скидку.

👉 Нажмите /start и завершите регистрацию.
                """,
                'inn': """
🔄 <b>Почти готово!</b>

Остался один шаг до получения вашего промокода −10% на отели Яндекс.Путешествий.

💼 Укажите ИНН вашей компании, чтобы активировать персональную скидку.

👉 Нажмите /start и завершите регистрацию.
                """,
                'confirmation': """
🔄 <b>Почти готово!</b>

Остался один шаг до получения вашего промокода −10% на отели Яндекс.Путешествий.

✅ Подтвердите участие в партнёрстве, чтобы активировать скидку.

👉 Нажмите /start и завершите регистрацию.
                """
            },
            'incomplete_3d': {
                'email': """
🎯 <b>Последний шаг!</b>

Вы всё ещё можете получить скидку −10% до 10 000 ₽ на бронирования отелей для своих туров.

⏳ Офер действует до 5 ноября.

👉 Нажмите /start и получите промокод сейчас.
                """,
                'inn': """
🎯 <b>Последний шаг!</b>

Вы всё ещё можете получить скидку −10% до 10 000 ₽ на бронирования отелей для своих туров.

⏳ Офер действует до 5 ноября.

👉 Нажмите /start и получите промокод сейчас.
                """,
                'confirmation': """
🎯 <b>Последний шаг!</b>

Вы всё ещё можете получить скидку −10% до 10 000 ₽ на бронирования отелей для своих туров.

⏳ Офер действует до 5 ноября.

👉 Нажмите /start и получите промокод сейчас.
                """
            }
        }
        
        return messages.get(reminder_type, {}).get(step, "")
    
    async def check_promo_reminders(self):
        """Проверка напоминаний о промокодах"""
        try:
            # Получаем пользователей, которые получили промокод 7 дней назад
            seven_days_ago = datetime.now() - timedelta(days=7)
            
            async with db.pool.acquire() as conn:
                # Проверяем, кому еще не отправляли напоминание о промокоде
                rows = await conn.fetch("""
                    SELECT u.user_id, u.promo_code, u.completed_at
                    FROM users u
                    LEFT JOIN user_reminders ur ON u.user_id = ur.user_id AND ur.reminder_type = 'promo_reminder'
                    WHERE u.completed_at IS NOT NULL 
                    AND u.promo_code IS NOT NULL
                    AND u.completed_at <= $1
                    AND ur.user_id IS NULL
                """, seven_days_ago)
                
                for row in rows:
                    await self.send_promo_reminder(row['user_id'], row['promo_code'])
                    await self.mark_reminder_sent(row['user_id'], 'promo_reminder')
                    
        except Exception as e:
            logger.error(f"Error checking promo reminders: {e}")
    
    async def send_promo_reminder(self, user_id: int, promo_code: str):
        """Отправляем напоминание о промокоде"""
        try:
            message = f"""
🎟️ <b>Напоминание: используйте ваш промокод {promo_code}!</b>

💡 Примените его при оплате отелей на Яндекс.Путешествиях — получите скидку до 10 000 ₽.

⏳ Действует до 5 ноября, успейте использовать!

📞 Если возникли вопросы — свяжитесь с поддержкой.
            """
            
            await self.bot.send_message(user_id, message, parse_mode="HTML")
            logger.info(f"Promo reminder sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending promo reminder to user {user_id}: {e}")
    
    async def reminder_already_sent(self, user_id: int, reminder_type: str) -> bool:
        """Проверяем, отправляли ли уже это напоминание"""
        try:
            async with db.pool.acquire() as conn:
                result = await conn.fetchval("""
                    SELECT 1 FROM user_reminders 
                    WHERE user_id = $1 AND reminder_type = $2
                """, user_id, reminder_type)
                
                return result is not None
                
        except Exception as e:
            logger.error(f"Error checking reminder status: {e}")
            return False
    
    async def mark_reminder_sent(self, user_id: int, reminder_type: str):
        """Отмечаем, что напоминание отправлено"""
        try:
            async with db.pool.acquire() as conn:
                # Создаем таблицу если не существует
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_reminders (
                        user_id BIGINT,
                        reminder_type TEXT,
                        sent_at TIMESTAMP DEFAULT NOW(),
                        PRIMARY KEY (user_id, reminder_type)
                    )
                """)
                
                await conn.execute("""
                    INSERT INTO user_reminders (user_id, reminder_type) 
                    VALUES ($1, $2)
                    ON CONFLICT (user_id, reminder_type) DO NOTHING
                """, user_id, reminder_type)
                
        except Exception as e:
            logger.error(f"Error marking reminder as sent: {e}")
    
    async def send_new_user_notification(self, user_id: int, email: str):
        """Уведомление админам о новом пользователе"""
        try:
            message = f"""
👤 <b>Новый пользователь</b>

ID: {user_id}
Email: {email}
Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}

📊 Проверьте статистику: /admin_stats
            """
            
            for admin_id in config.ADMIN_USER_IDS:
                try:
                    await self.bot.send_message(admin_id, message, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Failed to send new user notification to admin {admin_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending new user notification: {e}")
    
    async def send_completion_notification(self, user_id: int, email: str, promo_code: str):
        """Уведомление админам о завершенной регистрации"""
        try:
            message = f"""
✅ <b>Регистрация завершена</b>

ID: {user_id}
Email: {email}
Промокод: {promo_code}
Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}

📊 Проверьте статистику: /admin_stats
            """
            
            for admin_id in config.ADMIN_USER_IDS:
                try:
                    await self.bot.send_message(admin_id, message, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Failed to send completion notification to admin {admin_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending completion notification: {e}")

# Глобальный экземпляр
reminders = ReminderSystem()
