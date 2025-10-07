"""
YouTravel × Яндекс.Путешествия Telegram Bot
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from datetime import datetime

import config
from database import db
from sheets import sheets
from keyboards import get_main_menu, get_confirmation_keyboard, remove_keyboard, get_support_keyboard
from utils import validate_email, normalize_email, validate_inn, normalize_inn, mask_email, mask_inn
from monitoring import monitoring
from reminders import reminders

# Logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FSM States
class RegistrationStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_inn = State()
    waiting_for_confirmation = State()

class SupportStates(StatesGroup):
    waiting_for_support_message = State()

# Bot and Dispatcher
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# ============================================================================
# АДМИНСКИЕ КОМАНДЫ (ПЕРВЫМИ!)
# ============================================================================

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    """Админская панель"""
    logger.info("🔧 Admin command received!")
    user_id = message.from_user.id
    logger.info(f"🔧 User ID: {user_id}")
    
    if not is_admin(user_id):
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    # Получаем статистику
    stats = await db.get_stats()
    
    await message.answer(
        f"👨‍💼 <b>Админская панель</b>\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"• Всего пользователей: {stats['total_users']}\n"
        f"• Завершили регистрацию: {stats['completed_users']}\n"
        f"• Конверсия: {stats['conversion_rate']:.1f}%\n"
        f"• Выдано промокодов: {stats['promo_codes_issued']}\n\n"
        f"🔧 <b>Команды:</b>\n"
        f"• /admin_stats - детальная статистика\n"
        f"• /admin_users - список пользователей\n"
        f"• /admin_reset user_id - сбросить пользователя\n"
        f"• /admin_promos - проверить промокоды\n"
        f"• /admin_monitor - мониторинг системы\n"
        f"• /admin_reminders - управление напоминаниями\n"
        f"• /admin_message user_id текст - отправить сообщение\n"
        f"• /admin_reply user_id текст - ответить пользователю",
        parse_mode="HTML"
    )

@dp.message(Command("admin_stats"))
async def cmd_admin_stats(message: Message):
    """Детальная статистика"""
    logger.info("🔧 Admin_stats command received!")
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    # Получаем детальную статистику
    stats = await db.get_detailed_stats()
    
    await message.answer(
        f"📊 <b>Детальная статистика</b>\n\n"
        f"👥 <b>Пользователи:</b>\n"
        f"• Всего: {stats['total_users']}\n"
        f"• Завершили: {stats['completed_users']}\n"
        f"• В процессе: {stats['in_progress_users']}\n"
        f"• Конверсия: {stats['conversion_rate']:.1f}%\n\n"
        f"📅 <b>За последние 24 часа:</b>\n"
        f"• Новых пользователей: {stats['users_last_24h']}\n"
        f"• Завершили: {stats['completed_last_24h']}\n\n"
        f"🎟️ <b>Промокоды:</b>\n"
        f"• Выдано: {stats['promo_codes_issued']}\n"
        f"• Доступно: {stats['available_promos']}",
        parse_mode="HTML"
    )

@dp.message(Command("admin_users"))
async def cmd_admin_users(message: Message):
    """Список последних пользователей"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    # Получаем последних пользователей
    users = await db.get_recent_users(limit=10)
    
    if not users:
        await message.answer("📝 Пользователей пока нет.")
        return
    
    text = "👥 <b>Последние пользователи:</b>\n\n"
    for user in users:
        status = "✅" if user['completed_at'] else "⏳"
        date = user['created_at'].strftime("%d.%m %H:%M")
        username = f" @{user['telegram_username']}" if user['telegram_username'] else ""
        text += f"{status} ID: {user['user_id']}{username}\n"
        if user['email']:
            text += f"   📧 {mask_email(user['email'])}\n"
        if user['inn']:
            text += f"   🏢 {mask_inn(user['inn'])}\n"
        if user['promo_code']:
            text += f"   🎟️ {user['promo_code']}\n"
        text += f"   📅 {date}\n\n"
    
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("admin_reset"))
async def cmd_admin_reset(message: Message):
    """Сброс пользователя (админ)"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    # Парсим команду: /admin_reset <target_user_id>
    try:
        target_user_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer(
            "❌ Неверный формат команды.\n"
            "Использование: /admin_reset user_id"
        )
        return
    
    # Сбрасываем пользователя
    success = await db.delete_user(target_user_id)
    
    if success:
        await message.answer(f"✅ Пользователь {target_user_id} сброшен.")
        logger.info(f"Admin {user_id} reset user {target_user_id}")
    else:
        await message.answer(f"❌ Пользователь {target_user_id} не найден.")

@dp.message(Command("admin_promos"))
async def cmd_admin_promos(message: Message):
    """Проверка промокодов"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    try:
        # Получаем доступные промокоды
        available_promos = sheets.get_available_promo_codes()
        
        await message.answer(
            f"🎟️ <b>Доступные промокоды:</b>\n\n"
            f"Количество: {len(available_promos)}\n\n"
            f"Первые 5:\n" + "\n".join(available_promos[:5]),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка получения промокодов: {e}")

@dp.message(Command("admin_monitor"))
async def cmd_admin_monitor(message: Message):
    """Проверка мониторинга системы"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    try:
        # Проверяем здоровье системы
        health = await monitoring.check_system_health()
        metrics = await monitoring.check_metrics()
        
        # Формируем отчет
        report = f"🔍 <b>Мониторинг системы</b>\n\n"
        
        # Состояние системы
        report += f"🔧 <b>Состояние:</b>\n"
        report += f"• База данных: {'✅' if health['database'] else '❌'}\n"
        report += f"• Google Sheets: {'✅' if health['google_sheets'] else '❌'}\n"
        report += f"• Промокоды: {health['promo_codes']}\n\n"
        
        # Метрики
        stats = metrics.get('stats', {})
        report += f"📊 <b>Метрики:</b>\n"
        report += f"• Пользователей: {stats.get('total_users', 0)}\n"
        report += f"• Конверсия: {stats.get('conversion_rate', 0):.1f}%\n"
        report += f"• Доступно промокодов: {stats.get('available_promos', 0)}\n\n"
        
        # Алерты
        alerts = metrics.get('alerts', [])
        if alerts:
            report += f"⚠️ <b>Алерты:</b>\n"
            for alert in alerts:
                report += f"• {alert}\n"
        else:
            report += f"✅ <b>Все в порядке</b>\n"
        
        await message.answer(report, parse_mode="HTML")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка мониторинга: {e}")

@dp.message(Command("admin_reminders"))
async def cmd_admin_reminders(message: Message):
    """Управление напоминаниями"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    try:
        # Получаем статистику напоминаний
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
            
            # Статистика напоминаний
            total_reminders = await conn.fetchval("SELECT COUNT(*) FROM user_reminders")
            incomplete_users = await conn.fetchval("""
                SELECT COUNT(*) FROM users WHERE completed_at IS NULL
            """)
            
            # Незавершенные регистрации с деталями
            incomplete_details = await conn.fetch("""
                SELECT user_id, email, step, created_at, telegram_username
                FROM users 
                WHERE completed_at IS NULL
                ORDER BY created_at DESC
            """)
            
            # Отладочная информация
            logger.info(f"Found {len(incomplete_details)} incomplete registrations")
            
            # Последние напоминания
            recent_reminders = await conn.fetch("""
                SELECT user_id, reminder_type, sent_at 
                FROM user_reminders 
                ORDER BY sent_at DESC 
                LIMIT 5
            """)
        
        report = f"🔔 <b>Система напоминаний</b>\n\n"
        report += f"📊 <b>Статистика:</b>\n"
        report += f"• Всего отправлено: {total_reminders}\n"
        report += f"• Незавершенных регистраций: {incomplete_users}\n\n"
        
        # Детали незавершенных регистраций
        if incomplete_details:
            report += f"⏳ <b>Незавершенные регистрации:</b>\n"
            for user in incomplete_details:
                date = user['created_at'].strftime('%d.%m %H:%M')
                username = f"@{user['telegram_username']}" if user['telegram_username'] else "без username"
                email = mask_email(user['email']) if user['email'] else "не указан"
                step_names = {
                    'start': 'начало',
                    'email': 'ввод email',
                    'inn': 'ввод ИНН',
                    'confirmation': 'подтверждение'
                }
                step_name = step_names.get(user['step'], user['step'])
                report += f"• ID: {user['user_id']} ({username})\n"
                report += f"  📧 {email}\n"
                report += f"  📍 Этап: {step_name}\n"
                report += f"  📅 {date}\n\n"
        else:
            report += f"✅ <b>Все регистрации завершены!</b>\n\n"
        
        if recent_reminders:
            report += f"📝 <b>Последние напоминания:</b>\n"
            for reminder in recent_reminders:
                date = reminder['sent_at'].strftime('%d.%m %H:%M')
                report += f"• {reminder['reminder_type']} → {reminder['user_id']} ({date})\n"
        else:
            report += f"📝 <b>Напоминания:</b> Пока не отправлялись\n"
        
        report += f"\n⏰ <b>Интервалы:</b>\n"
        report += f"• Через 1 час после начала\n"
        report += f"• Через 24 часа\n"
        report += f"• Через 3 дня\n"
        report += f"• Напоминание о промокоде через 7 дней\n"
        
        await message.answer(report, parse_mode="HTML")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка получения статистики напоминаний: {e}")


@dp.message(Command("admin_message"))
async def cmd_admin_message(message: Message):
    """Админ: отправить сообщение пользователю"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        # Парсим команду: /admin_message user_id текст_сообщения
        parts = message.text.split(' ', 2)
        if len(parts) < 3:
            await message.answer(
                "❌ Неверный формат команды.\n"
                "Использование: /admin_message user_id текст_сообщения\n"
                "Пример: /admin_message 229392200 Привет! Заверши регистрацию."
            )
            return
        
        user_id = int(parts[1])
        text = parts[2]
        
        # Отправляем сообщение
        await bot.send_message(user_id, text, parse_mode="HTML")
        await message.answer(f"✅ Сообщение отправлено пользователю {user_id}")
        
    except ValueError:
        await message.answer("❌ Неверный user_id. Должен быть числом.")
    except Exception as e:
        logger.error(f"Error sending admin message: {e}")
        await message.answer(f"❌ Ошибка при отправке сообщения: {e}")


@dp.message(Command("admin_reply"))
async def cmd_admin_reply(message: Message):
    """Админ: ответить пользователю от имени поддержки"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        # Парсим команду: /admin_reply user_id текст_ответа
        parts = message.text.split(' ', 2)
        if len(parts) < 3:
            await message.answer(
                "❌ Неверный формат команды.\n"
                "Использование: /admin_reply user_id текст_ответа\n"
                "Пример: /admin_reply 229392200 Спасибо за обращение! Мы поможем вам."
            )
            return
        
        user_id = int(parts[1])
        reply_text = parts[2]
        
        # Отправляем ответ от имени поддержки
        support_reply = f"""
💬 <b>Ответ от поддержки</b>

{reply_text}

---
👤 Поддержка YouTravel × Яндекс.Путешествия
"""
        
        await bot.send_message(user_id, support_reply, parse_mode="HTML")
        await message.answer(f"✅ Ответ отправлен пользователю {user_id}")
        
    except ValueError:
        await message.answer("❌ Неверный user_id. Должен быть числом.")
    except Exception as e:
        logger.error(f"Error sending admin reply: {e}")
        await message.answer(f"❌ Ошибка при отправке ответа: {e}")


# ============================================================================
# КОМАНДЫ И МЕНЮ
# ============================================================================

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Проверяем существует ли пользователь
    user = await db.get_user(user_id)
    
    if user and user.get('completed_at'):
        # Пользователь уже завершил регистрацию
        promo_code = user.get('promo_code')
        await message.answer(
            f"👋 С возвращением!\n\n"
            f"✅ Вы уже зарегистрированы в Яндекс.Путешествиях\n"
            f"🎟️ Ваш промокод: <code>{promo_code}</code>\n\n"
            f"📋 Промокод даёт скидку 10% (до 10 000 ₽) на первое бронирование.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        return
    
    # Новый пользователь или незавершённая регистрация
    await db.create_user(user_id, username)
    
    # Уведомляем админов о новом пользователе
    await reminders.send_new_user_notification(user_id, "Новый пользователь")
    
    await message.answer(
        "👋 Привет! Это бот для регистрации в <b>B2B Яндекс.Путешествий</b>.\n\n"
        "🎁 После регистрации вы получите промокод на <b>−10% (до 10 000 ₽)</b> "
        "на первое бронирование!\n\n"
        "📝 Для начала, введите ваш email, который вы использовали при регистрации на YouTravel:",
        reply_markup=remove_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(RegistrationStates.waiting_for_email)
    logger.info(f"User {user_id} started registration")

@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    """Обработчик команды /menu"""
    await message.answer(
        "📱 Главное меню:",
        reply_markup=get_main_menu()
    )

@dp.message(Command("status"))
@dp.message(F.text == "📊 Мой статус")
async def cmd_status(message: Message):
    """Обработчик команды /status"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await message.answer(
            "❌ Вы ещё не начали регистрацию.\n"
            "Нажмите /start для начала.",
            reply_markup=get_main_menu()
        )
        return
    
    if user.get('completed_at'):
        completed_date = user['completed_at'].strftime("%d.%m.%Y %H:%M")
        await message.answer(
            f"✅ <b>Регистрация завершена</b>\n\n"
            f"📧 Email: {mask_email(user['email'])}\n"
            f"🏢 ИНН: {mask_inn(user['inn'])}\n"
            f"🎟️ Промокод: <code>{user['promo_code']}</code>\n"
            f"📅 Дата: {completed_date}\n\n"
            f"Промокод даёт скидку 10% (до 10 000 ₽) на первое бронирование.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    else:
        step_names = {
            'email': '📧 Ввод email',
            'inn': '🏢 Ввод ИНН',
            'confirmation': '✅ Подтверждение'
        }
        current_step = step_names.get(user.get('step', 'start'), 'Начало')
        
        await message.answer(
            f"⏳ <b>Регистрация не завершена</b>\n\n"
            f"📍 Текущий шаг: {current_step}\n\n"
            f"Продолжите регистрацию, следуя инструкциям бота.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )

@dp.message(Command("help"))
@dp.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "❓ <b>Помощь</b>\n\n"
        "Этот бот помогает зарегистрироваться в B2B программе Яндекс.Путешествий "
        "и получить промокод на скидку.\n\n"
        "<b>Команды:</b>\n"
        "/start - Начать регистрацию\n"
        "/status - Проверить статус регистрации\n"
        "/menu - Показать главное меню\n"
        "/help - Показать эту справку\n\n"
        "<b>Процесс регистрации:</b>\n"
        "1️⃣ Введите email от YouTravel\n"
        "2️⃣ Зарегистрируйтесь в Яндекс.Путешествиях\n"
        "3️⃣ Введите ИНН вашей компании\n"
        "4️⃣ Получите промокод!\n\n"
        "💬 Если возникли вопросы - свяжитесь с поддержкой.",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

@dp.message(F.text == "💬 Поддержка")
async def cmd_support(message: Message):
    """Обработчик кнопки поддержки"""
    await message.answer(
        f"💬 <b>Поддержка</b>\n\n"
        f"Если у вас возникли вопросы или проблемы, вы можете:\n\n"
        f"📝 Написать сообщение в поддержку прямо здесь\n"
        f"👤 Или связаться с @maria_youtravel напрямую",
        reply_markup=get_support_keyboard(),
        parse_mode="HTML"
    )

@dp.message(F.text == "📝 Написать в поддержку")
async def start_support_chat(message: Message, state: FSMContext):
    """Начать переписку с поддержкой"""
    await message.answer(
        "📝 <b>Написать в поддержку</b>\n\n"
        "Опишите ваш вопрос или проблему, и мы обязательно поможем!\n\n"
        "💡 Чем подробнее вы опишете ситуацию, тем быстрее мы сможем помочь.",
        reply_markup=remove_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(SupportStates.waiting_for_support_message)
    logger.info(f"User {message.from_user.id} started support chat")

@dp.message(F.text == "🔙 Назад в меню")
async def back_to_menu(message: Message, state: FSMContext):
    """Вернуться в главное меню"""
    await state.clear()
    await message.answer(
        "📱 Главное меню:",
        reply_markup=get_main_menu()
    )

@dp.message(F.text.in_(["📝 Написать в поддержку", "💬 Поддержка"]))
async def handle_support_menu_messages(message: Message, state: FSMContext):
    """Обработка сообщений в меню поддержки"""
    if message.text == "📝 Написать в поддержку":
        await start_support_chat(message, state)
    elif message.text == "💬 Поддержка":
        await cmd_support(message)

@dp.message(SupportStates.waiting_for_support_message)
async def process_support_message(message: Message, state: FSMContext):
    """Обработка сообщения в поддержку"""
    user_id = message.from_user.id
    username = message.from_user.username
    user_text = message.text
    
    # Отправляем сообщение админам
    support_message = f"""
🆘 <b>Новое сообщение в поддержку</b>

👤 <b>Пользователь:</b> {user_id}
📝 <b>Username:</b> @{username if username else 'не указан'}
💬 <b>Сообщение:</b>
{user_text}

📅 <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
    
    # Отправляем всем админам
    for admin_id in config.ADMIN_USER_IDS:
        try:
            await bot.send_message(admin_id, support_message, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error sending support message to admin {admin_id}: {e}")
    
    # Подтверждаем пользователю
    await message.answer(
        "✅ <b>Сообщение отправлено!</b>\n\n"
        "Мы получили ваше обращение и обязательно ответим в ближайшее время.\n\n"
        "⏰ Обычно мы отвечаем в течение 1-2 часов в рабочее время.",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    
    await state.clear()
    logger.info(f"Support message from user {user_id} sent to admins")

@dp.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    """Сброс регистрации (только для админов)"""
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь админом
    if not is_admin(user_id):
        await message.answer(
            "❌ У вас нет прав для сброса регистрации.\n"
            "Обратитесь к @maria_youtravel для помощи."
        )
        return
    
    logger.info(f"Admin {user_id} requested reset")
    
    # Удаляем пользователя из базы
    try:
        # Проверяем существует ли пользователь
        user = await db.get_user(user_id)
        
        if not user:
            logger.info(f"User {user_id} not found in database (nothing to reset)")
            await message.answer(
                "ℹ️ У вас нет активной регистрации.\n\n"
                "Отправьте /start чтобы начать регистрацию.",
                reply_markup=remove_keyboard(),
                parse_mode="HTML"
            )
            return
        
        logger.info(f"Deleting user {user_id} from database...")
        
        async with db.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM users WHERE user_id = $1",
                user_id
            )
        
        logger.info(f"✓ User {user_id} deleted: {result}")
        
        # Очищаем состояние FSM
        await state.clear()
        logger.info(f"✓ FSM state cleared for user {user_id}")
        
        await message.answer(
            "🔄 <b>Регистрация сброшена!</b>\n\n"
            "Теперь вы можете начать заново.\n"
            "Отправьте /start для новой регистрации.",
            reply_markup=remove_keyboard(),
            parse_mode="HTML"
        )
        
        logger.info(f"✅ User {user_id} reset successful")
        
    except Exception as e:
        logger.error(f"❌ Error resetting user {user_id}: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        await message.answer(
            f"❌ Ошибка при сбросе регистрации.\n\n"
            f"Ошибка: {type(e).__name__}\n"
            f"Попробуйте ещё раз или свяжитесь с @maria_youtravel",
            reply_markup=get_main_menu()
        )

# ============================================================================
# РЕГИСТРАЦИЯ - ШАГ 1: EMAIL
# ============================================================================

@dp.message(RegistrationStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    """Обработка ввода email"""
    email = message.text.strip()
    user_id = message.from_user.id
    
    # Валидация формата
    if not validate_email(email):
        await message.answer(
            "❌ Неверный формат email.\n\n"
            "Пожалуйста, введите корректный email адрес:"
        )
        return
    
    # Нормализация
    email = normalize_email(email)
    
    # Проверка наличия в базе YouTravel
    if not sheets.check_email_exists(email):
        await message.answer(
            f"❌ Email <code>{email}</code> не найден в базе YouTravel.\n\n"
            f"Убедитесь, что вы:\n"
            f"• Зарегистрированы на YouTravel.me\n"
            f"• Ввели email правильно\n\n"
            f"Попробуйте ещё раз или свяжитесь с @maria_youtravel",
            parse_mode="HTML"
        )
        return
    
    # Сохраняем email
    await db.update_user(user_id, email=email, step='inn')
    
    # Переходим к следующему шагу
    await message.answer(
        f"✅ Email подтверждён!\n\n"
        f"📋 <b>Следующий шаг:</b>\n"
        f"Зарегистрируйтесь в B2B Яндекс.Путешествий:\n"
        f"🔗 https://passport.yandex.ru/auth/reg/org?origin=travel_unmanaged&retpath=https://id.yandex.ru/org/members\n\n"
        f"После регистрации введите <b>ИНН вашей компании</b> (10 или 12 цифр):",
        parse_mode="HTML"
    )
    
    await state.set_state(RegistrationStates.waiting_for_inn)
    logger.info(f"User {user_id} confirmed email: {mask_email(email)}")

# ============================================================================
# РЕГИСТРАЦИЯ - ШАГ 2: ИНН
# ============================================================================

@dp.message(RegistrationStates.waiting_for_inn)
async def process_inn(message: Message, state: FSMContext):
    """Обработка ввода ИНН"""
    inn = message.text.strip()
    user_id = message.from_user.id
    
    # Валидация формата
    if not validate_inn(inn):
        await message.answer(
            "❌ Неверный формат ИНН.\n\n"
            "ИНН должен содержать 10 или 12 цифр.\n"
            "Попробуйте ещё раз:"
        )
        return
    
    # Нормализация
    inn = normalize_inn(inn)
    
    # Проверка на дубликаты
    if await db.check_inn_exists(inn):
        await message.answer(
            f"❌ ИНН <code>{mask_inn(inn)}</code> уже зарегистрирован.\n\n"
            f"Каждая компания может зарегистрироваться только один раз.\n"
            f"Если это ошибка, свяжитесь с @maria_youtravel",
            parse_mode="HTML"
        )
        return
    
    # Сохраняем данные во временное состояние
    await state.update_data(inn=inn)
    
    # Получаем данные пользователя
    user = await db.get_user(user_id)
    email = user.get('email')
    
    # Запрашиваем подтверждение
    await message.answer(
        f"📋 <b>Проверьте данные:</b>\n\n"
        f"📧 Email: <code>{email}</code>\n"
        f"🏢 ИНН: <code>{inn}</code>\n\n"
        f"Всё верно?",
        reply_markup=get_confirmation_keyboard(),
        parse_mode="HTML"
    )
    
    await state.set_state(RegistrationStates.waiting_for_confirmation)
    logger.info(f"User {user_id} entered INN: {mask_inn(inn)}")

# ============================================================================
# РЕГИСТРАЦИЯ - ШАГ 3: ПОДТВЕРЖДЕНИЕ
# ============================================================================

@dp.callback_query(F.data == "confirm_yes", RegistrationStates.waiting_for_confirmation)
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    """Подтверждение данных и выдача промокода"""
    user_id = callback.from_user.id
    
    # Получаем ИНН из состояния
    data = await state.get_data()
    inn = data.get('inn')
    
    # Получаем промокод
    promo_code = sheets.get_available_promo()
    
    if not promo_code:
        await callback.message.edit_text(
            "❌ <b>Ошибка</b>\n\n"
            "К сожалению, промокоды временно закончились.\n"
            f"Пожалуйста, свяжитесь с @maria_youtravel",
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # Сохраняем в БД
    await db.update_user(
        user_id,
        inn=inn,
        promo_code=promo_code,
        step='completed',
        completed_at=datetime.now()
    )
    
    # Очищаем состояние
    await state.clear()
    
    # Отправляем промокод
    await callback.message.edit_text(
        f"🎉 <b>Поздравляем! Регистрация завершена!</b>\n\n"
        f"🎟️ Ваш промокод: <code>{promo_code}</code>\n\n"
        f"💰 Промокод даёт скидку <b>−10% (до 10 000 ₽)</b> на первое бронирование в Яндекс.Путешествиях.\n\n"
        f"🔗 Используйте его при оформлении заказа:\n"
        f"https://travel.yandex.ru/b2b\n\n"
        f"✈️ Приятных путешествий!",
        parse_mode="HTML"
    )
    
    # Показываем главное меню
    await callback.message.answer(
        "📱 Главное меню:",
        reply_markup=get_main_menu()
    )
    
    # Уведомляем админов о завершенной регистрации
    await reminders.send_completion_notification(user_id, user['email'], promo_code)
    
    await callback.answer("✅ Регистрация завершена!")
    logger.info(f"User {user_id} completed registration with promo: {promo_code}")

@dp.callback_query(F.data == "confirm_no", RegistrationStates.waiting_for_confirmation)
async def reject_confirmation(callback: CallbackQuery, state: FSMContext):
    """Отказ от подтверждения - начать заново"""
    await callback.message.edit_text(
        "🔄 Хорошо, давайте начнём заново.\n\n"
        "Введите ваш email от YouTravel:"
    )
    
    await state.set_state(RegistrationStates.waiting_for_email)
    await callback.answer("Начинаем сначала")
    logger.info(f"User {callback.from_user.id} restarted registration")

# ============================================================================
# ОБРАБОТКА НЕИЗВЕСТНЫХ СООБЩЕНИЙ
# ============================================================================

@dp.message()
async def unknown_message(message: Message):
    """Обработка неизвестных сообщений"""
    text = message.text.lower()
    
    # Проверяем, не является ли это сообщением в поддержку
    support_keywords = ['поддержка', 'помощь', 'проблема', 'вопрос', 'ошибка', 'не работает', 'не получается', 'тестовое сообщение']
    if any(keyword in text for keyword in support_keywords):
        # Перенаправляем в поддержку
        await message.answer(
            "💬 <b>Похоже, вам нужна помощь!</b>\n\n"
            "Для обращения в поддержку нажмите кнопку ниже:",
            reply_markup=get_support_keyboard(),
            parse_mode="HTML"
        )
        return
    
    await message.answer(
        "❓ Я не понимаю эту команду.\n\n"
        "Используйте /help для просмотра доступных команд.",
        reply_markup=get_main_menu()
    )

# ============================================================================
# АДМИНСКИЕ КОМАНДЫ
# ============================================================================

def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь админом"""
    logger.info(f"🔍 Checking admin for user {user_id}, admin IDs: {config.ADMIN_USER_IDS}")
    result = user_id in config.ADMIN_USER_IDS
    logger.info(f"🔍 Admin check result: {result}")
    return result

# Удалены дублирующие обработчики

# ============================================================================
# ЗАПУСК БОТА
# ============================================================================

async def main():
    """Главная функция запуска бота"""
    try:
        # Подключаемся к БД
        await db.connect()
        
        # Подключаемся к Google Sheets
        sheets.connect()
        
        logger.info("🤖 Bot started with admin panel")
        logger.info(f"🔧 Admin IDs: {config.ADMIN_USER_IDS}")
        logger.info(f"🔧 Admin IDs type: {type(config.ADMIN_USER_IDS)}")
        
        # Запускаем мониторинг в фоне
        monitoring_task = asyncio.create_task(monitoring.start_monitoring(bot))
        
        # Запускаем систему напоминаний в фоне
        reminders_task = asyncio.create_task(reminders.start_reminders(bot))
        
        # Запускаем polling
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        # Останавливаем мониторинг
        if 'monitoring_task' in locals():
            monitoring_task.cancel()
        await db.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

# Force restart
