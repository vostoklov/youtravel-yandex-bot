# 🤖 YouTravel × Яндекс.Путешествия Bot

Telegram-бот для регистрации B2B агентств в Яндекс.Путешествиях с выдачей промокодов -10% (кэп 10K₽).

## 🚀 Быстрый старт

### Для новых разработчиков
1. **Прочитайте**: [ONBOARDING.md](./ONBOARDING.md) - полный гайд
2. **Клонируйте**: `git clone https://github.com/vostoklov/youtravel-yandex-bot.git`
3. **Настройте**: `cp .env.example .env` и заполните переменные
4. **Запустите**: `python3 bot.py`

### Для пользователей
- **Telegram**: [@YouTravelYandexBot](https://t.me/YouTravelYandexBot)
- **Команды**: `/start`, `/status`, `/help`, `/reset`

## 📊 Статус проекта

| Компонент | Статус |
|-----------|--------|
| 🤖 Telegram Bot | ✅ Работает |
| 🗄️ PostgreSQL | ✅ Подключен |
| 📊 Google Sheets | ✅ Подключен |
| 🎟️ Промокоды | ✅ Выдаются |
| 🔗 Регистрация | ✅ Работает |
| 🧪 Тестирование | ✅ Пройдено |

## 🏗️ Архитектура

```
Telegram Bot (aiogram) ↔ PostgreSQL (Railway) ↔ Google Sheets (2 таблицы)
```

## 📁 Основные файлы

- `bot.py` - основной бот
- `database.py` - работа с PostgreSQL
- `sheets.py` - работа с Google Sheets
- `config.py` - конфигурация
- `ONBOARDING.md` - гайд для разработчиков

## 🔧 Полезные команды

```bash
# Тест подключения
python3 test_sheets_connection.py

# Сброс пользователя
python3 reset_user.py list

# Логи Railway
railway logs --lines 100
```

## 📞 Контакты

- **GitHub**: [vostoklov/youtravel-yandex-bot](https://github.com/vostoklov/youtravel-yandex-bot)
- **Railway**: [youtravel-yandex-bot](https://railway.app/project/youtravel-yandex-bot)
- **Support**: @vostoklov

## 📚 Документация

- [ONBOARDING.md](./ONBOARDING.md) - Полный гайд для разработчиков
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Чеклист деплоя
- [TESTING_GUIDE.md](./TESTING_GUIDE.md) - Гайд по тестированию

---

**Цель**: Собрать ≥100 регистраций B2B агентств 🎯