"""
Клавиатуры для бота
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Мой статус")],
            [KeyboardButton(text="ℹ️ Помощь"), KeyboardButton(text="💬 Поддержка")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, верно", callback_data="confirm_yes"),
                InlineKeyboardButton(text="❌ Изменить", callback_data="confirm_no")
            ]
        ]
    )
    return keyboard

def remove_keyboard() -> ReplyKeyboardRemove:
    """Убрать клавиатуру"""
    return ReplyKeyboardRemove()
