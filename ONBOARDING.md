# 🚀 Onboarding Guide для разработчиков

## 📋 Обзор проекта

**YouTravel × Яндекс.Путешествия Telegram Bot**  
Цель: Собрать ≥100 регистраций B2B агентств и выдать промокоды -10% (кэп 10K₽)

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │   PostgreSQL    │    │  Google Sheets  │
│   (aiogram 3.x) │◄──►│   (Railway)     │    │  (2 таблицы)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Структура проекта

```
youtravel-yandex-bot/
├── bot.py              # Основной бот (aiogram)
├── database.py         # PostgreSQL операции
├── sheets.py           # Google Sheets API
├── config.py           # Конфигурация
├── keyboards.py        # Telegram клавиатуры
├── utils.py            # Утилиты
├── requirements.txt    # Зависимости
├── .env               # Локальные переменные (НЕ в git)
└── credentials.json   # Google Service Account (НЕ в git)
```

## 🔧 Локальная разработка

### 1. Клонирование
```bash
git clone https://github.com/vostoklov/youtravel-yandex-bot.git
cd youtravel-yandex-bot
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка .env
Скопировать `.env.example` и заполнить:
```bash
cp .env.example .env
```

**Обязательные переменные:**
```env
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://user:pass@host:port/db
GOOGLE_CREDENTIALS_JSON=path_to_credentials.json
GOOGLE_SHEET_EMAILS_ID=1xBFSvBBdKG27YAAfjMy6K0dEcFP4pQMUujpblK8tub0
GOOGLE_SHEET_PROMOS_ID=1RQvWCLGUocLTJqyBdwCRCEXnUkNmABhL7ng9-paLh6E
```

### 4. Google Sheets доступ
1. Получить `credentials.json` от владельца проекта
2. Добавить service account email в Google Sheets:
   - `claude-by-ivan-bortnikov@probable-bebop-305708.iam.gserviceaccount.com`
   - Роль: **Editor**

### 5. Тестирование
```bash
# Тест подключения к Google Sheets
python3 test_sheets_connection.py

# Тест сброса пользователя (если нужно)
python3 reset_user.py list
python3 reset_user.py <telegram_id>
```

## 🚀 Деплой

### Railway (автоматический)
```bash
git push origin main
# Railway автоматически задеплоит
```

### Проверка деплоя
```bash
railway logs --lines 50
```

## 📊 База данных

### Схема таблицы `users`:
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,           -- Telegram ID
    telegram_username TEXT,               -- @username
    email TEXT,                          -- Email от YouTravel
    inn TEXT,                            -- ИНН компании
    promo_code TEXT,                     -- Выданный промокод
    step TEXT DEFAULT 'start',           -- Текущий шаг
    created_at TIMESTAMP DEFAULT NOW(),  -- Дата создания
    completed_at TIMESTAMP,              -- Дата завершения
    UNIQUE(inn)                          -- Один ИНН = одна регистрация
);
```

### Полезные SQL запросы:
```sql
-- Статистика
SELECT 
    COUNT(*) as total_users,
    COUNT(completed_at) as completed,
    ROUND(COUNT(completed_at) * 100.0 / COUNT(*), 2) as conversion_rate
FROM users;

-- Последние регистрации
SELECT user_id, email, inn, promo_code, completed_at 
FROM users 
ORDER BY created_at DESC 
LIMIT 10;

-- Сброс пользователя (для тестирования)
DELETE FROM users WHERE user_id = YOUR_TELEGRAM_ID;
```

## 🔄 Flow бота

### 1. `/start`
- Проверка существующей регистрации
- Если есть → показать промокод
- Если нет → начать регистрацию

### 2. Ввод email
- Валидация формата
- Проверка в Google Sheets (таблица Emails)
- Сохранение в БД

### 3. Регистрация в Яндекс.Путешествиях
- Ссылка: https://passport.yandex.ru/auth/reg/org?origin=travel_unmanaged&retpath=https://id.yandex.ru/org/members
- Пользователь регистрируется самостоятельно

### 4. Ввод ИНН
- Валидация (10 или 12 цифр)
- Проверка на дубликаты
- Подтверждение данных

### 5. Выдача промокода
- Получение из Google Sheets (таблица Promos)
- Сохранение в БД
- Отправка пользователю

## 🛠️ Полезные команды

### Бот команды:
- `/start` - Начать регистрацию
- `/status` - Проверить статус
- `/menu` - Главное меню
- `/help` - Справка
- `/reset` - Сбросить регистрацию (DEV)

### Локальные скрипты:
```bash
# Тест подключения
python3 test_sheets_connection.py

# Проверка структуры таблиц
python3 check_sheets_structure.py

# Подготовка JSON для Railway
python3 prepare_railway_credentials.py

# Сброс пользователя
python3 reset_user.py list
python3 reset_user.py <telegram_id>
```

## 📈 Мониторинг

### Railway логи:
```bash
railway logs --lines 100
railway logs --filter "@level:error"
```

### Ключевые метрики:
- Количество регистраций
- Конверсия (завершенные / начатые)
- Ошибки подключения к Google Sheets
- Ошибки базы данных

## 🐛 Траблшутинг

### Частые проблемы:

#### 1. Google Sheets 403 Error
```
APIError: [403]: The caller does not have permission
```
**Решение**: Добавить service account email в таблицы с ролью Editor

#### 2. Database connection error
```
asyncpg.exceptions.ConnectionDoesNotExistError
```
**Решение**: Проверить `DATABASE_URL` на Railway

#### 3. UndefinedColumnError
```
UndefinedColumnError: column "telegram_id" does not exist
```
**Решение**: Использовать `user_id` вместо `telegram_id`

#### 4. Bot not responding
**Решение**: Проверить `BOT_TOKEN` и логи Railway

## 📞 Контакты

- **Репозиторий**: https://github.com/vostoklov/youtravel-yandex-bot
- **Railway**: https://railway.app/project/youtravel-yandex-bot
- **Telegram Bot**: @YouTravelYandexBot
- **Support**: @vostoklov

## 📚 Дополнительная документация

- `DEPLOYMENT_CHECKLIST.md` - Чеклист деплоя
- `SUMMARY.md` - Краткая сводка проекта
- `TESTING_GUIDE.md` - Гайд по тестированию
- `FIX_GOOGLE_SHEETS_ACCESS.md` - Инструкция по доступу

## 🎯 Следующие задачи

1. **Мониторинг метрик** - отслеживание регистраций
2. **A/B тестирование** - разные варианты сообщений
3. **Аналитика** - детальная статистика
4. **Уведомления** - алерты при ошибках
5. **Масштабирование** - оптимизация для больших нагрузок

---

**Удачи в разработке! 🚀**
