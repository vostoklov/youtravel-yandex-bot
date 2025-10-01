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
from keyboards import get_main_menu, get_confirmation_keyboard, remove_keyboard
from utils import validate_email, normalize_email, validate_inn, normalize_inn, mask_email, mask_inn

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

# Bot and Dispatcher
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

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
        f"Если у вас возникли вопросы или проблемы, напишите:\n"
        f"👤 @{config.SUPPORT_USERNAME}",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
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
            f"Попробуйте ещё раз или свяжитесь с @{config.SUPPORT_USERNAME}",
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
            f"Если это ошибка, свяжитесь с @{config.SUPPORT_USERNAME}",
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
            f"Пожалуйста, свяжитесь с @{config.SUPPORT_USERNAME}",
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
    await message.answer(
        "❓ Я не понимаю эту команду.\n\n"
        "Используйте /help для просмотра доступных команд.",
        reply_markup=get_main_menu()
    )

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
        
        logger.info("🤖 Bot started")
        
        # Запускаем polling
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await db.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

