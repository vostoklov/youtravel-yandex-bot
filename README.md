# YouTravel × Яндекс.Путешествия Telegram Bot

Telegram бот для регистрации в B2B программе Яндекс.Путешествий и получения промокодов.

## 🚀 Функционал

- ✅ Проверка email в базе YouTravel
- ✅ Регистрация в Яндекс.Путешествиях
- ✅ Валидация ИНН компании
- ✅ Автоматическая выдача промокодов
- ✅ Защита от дубликатов (один ИНН = одна регистрация)
- ✅ Статистика и аналитика

## 📋 Требования

- Python 3.10+
- PostgreSQL database
- Google Sheets API доступ
- Telegram Bot Token

## 🛠️ Установка

### 1. Клонировать репозиторий

```bash
git clone <repo-url>
cd youtravel_bot
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Настроить переменные окружения

Создайте файл `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://user:password@host:port/dbname
GOOGLE_SHEET_EMAILS_ID=your_emails_sheet_id
GOOGLE_SHEET_PROMOS_ID=your_promos_sheet_id
GOOGLE_CREDENTIALS_JSON=credentials.json
SUPPORT_USERNAME=your_telegram_username
```

### 4. Добавить credentials.json

Поместите файл `credentials.json` от Google Service Account в корень проекта.

### 5. Запустить бота

```bash
python bot.py
```

## 🌐 Деплой на Railway

### 1. Создать проект на Railway

1. Зайти на https://railway.app
2. Создать новый проект
3. Подключить GitHub репозиторий

### 2. Добавить PostgreSQL

1. В проекте нажать "+ New"
2. Выбрать "Database" → "PostgreSQL"
3. Railway автоматически создаст `DATABASE_URL`

### 3. Добавить переменные окружения

В разделе "Variables" добавить:
- `BOT_TOKEN`
- `GOOGLE_SHEET_EMAILS_ID`
- `GOOGLE_SHEET_PROMOS_ID`
- `SUPPORT_USERNAME`
- `ENVIRONMENT=production`

### 4. Добавить credentials.json

Содержимое файла `credentials.json` добавить как переменную `GOOGLE_CREDENTIALS_JSON` или загрузить файл напрямую.

### 5. Deploy

Railway автоматически задеплоит бота после push в GitHub.

## 📊 Google Sheets структура

### Таблица Emails (YouTravel Emails Database)

| email | name |
|-------|------|
| user@example.com | Имя Фамилия |

### Таблица Promos (YouTravel Promo Codes)

| promo_code | is_used |
|------------|---------|
| YT-B2B-ABC123 | FALSE |
| YT-B2B-DEF456 | TRUE |

## 🗄️ База данных

Структура таблицы `users`:

```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    telegram_username TEXT,
    email TEXT,
    inn TEXT UNIQUE,
    promo_code TEXT,
    step TEXT DEFAULT 'start',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

## 📝 Команды бота

- `/start` - Начать регистрацию
- `/status` - Проверить статус регистрации  
- `/menu` - Показать главное меню
- `/help` - Показать справку

## 🔧 Структура проекта

```
youtravel_bot/
├── bot.py              # Основной файл бота
├── config.py           # Конфигурация
├── database.py         # Работа с PostgreSQL
├── sheets.py           # Работа с Google Sheets
├── keyboards.py        # Клавиатуры Telegram
├── utils.py            # Утилиты (валидация, форматирование)
├── requirements.txt    # Зависимости Python
├── Procfile           # Для Railway
├── .env               # Переменные окружения (не в Git)
├── .gitignore         # Игнорируемые файлы
├── credentials.json   # Google Service Account (не в Git)
└── README.md          # Документация
```

## 📈 Мониторинг

Логи бота доступны в Railway Dashboard → Deploy Logs

Статистика доступна через команду `/status` для администраторов.

## 🐛 Troubleshooting

### Бот не отвечает
- Проверьте что бот запущен (Railway Deployments)
- Проверьте логи на наличие ошибок
- Убедитесь что `BOT_TOKEN` правильный

### Ошибки с БД
- Проверьте `DATABASE_URL` в переменных
- Убедитесь что PostgreSQL запущен

### Ошибки с Google Sheets
- Проверьте что Service Account имеет доступ к таблицам
- Проверьте правильность ID таблиц
- Убедитесь что Google Sheets API и Drive API включены

## 📞 Поддержка

По вопросам: @vostoklov

## 📄 Лицензия

MIT
