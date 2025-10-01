# 🛠️ Developer Setup - Безопасная настройка для разработчиков

## ⚠️ ВАЖНО: Безопасность

**НЕ ИСПОЛЬЗУЙТЕ** продакшн credentials в разработке!

## 🔧 Настройка тестовой среды

### 1️⃣ **Telegram Bot (тестовый)**

1. Открыть [@BotFather](https://t.me/BotFather)
2. `/newbot`
3. **Имя**: `YouTravel Test Bot`
4. **Username**: `YouTravelTestBot` (или любой доступный)
5. **Скопировать токен** → использовать в `.env`

### 2️⃣ **Google Sheets (тестовые таблицы)**

#### Создать копии таблиц:
1. **Emails таблица**: Создать копию продакшн таблицы
2. **Promos таблица**: Создать копию с тестовыми промокодами
3. **Получить новые ID** таблиц

#### Тестовые данные:
```
Emails таблица:
| Email                | Name           |
|----------------------|----------------|
| test1@example.com    | Тест Тестов    |
| test2@example.com    | Тест Тестова   |
| developer@test.com   | Разработчик    |

Promos таблица:
| Promo Code      |
|-----------------|
| TEST-PROMO-001  |
| TEST-PROMO-002  |
| TEST-PROMO-003  |
```

### 3️⃣ **Google Service Account (тестовый)**

1. Создать **новый Service Account** в Google Cloud Console
2. Скачать **credentials.json**
3. Дать доступ **только к тестовым таблицам**
4. **НЕ давать доступ** к продакшн таблицам

### 4️⃣ **База данных (локальная)**

#### Вариант A: Локальная PostgreSQL
```bash
# Установка PostgreSQL
brew install postgresql
brew services start postgresql

# Создание базы
createdb youtravel_test

# DATABASE_URL для .env
DATABASE_URL=postgresql://username:password@localhost:5432/youtravel_test
```

#### Вариант B: Тестовая БД на Railway
1. Создать **новый проект** на Railway
2. Добавить **PostgreSQL service**
3. Использовать **тестовую DATABASE_URL**

## 📋 .env для разработки

```env
# Telegram Bot (ТЕСТОВЫЙ!)
BOT_TOKEN=YOUR_TEST_BOT_TOKEN_FROM_BOTFATHER

# Database (ЛОКАЛЬНАЯ ИЛИ ТЕСТОВАЯ!)
DATABASE_URL=postgresql://username:password@localhost:5432/youtravel_test

# Google Sheets (ТЕСТОВЫЕ ТАБЛИЦЫ!)
GOOGLE_SHEET_EMAILS_ID=YOUR_TEST_EMAILS_TABLE_ID
GOOGLE_SHEET_PROMOS_ID=YOUR_TEST_PROMOS_TABLE_ID
GOOGLE_CREDENTIALS_JSON=path/to/test/credentials.json

# Support
SUPPORT_USERNAME=your_username

# Environment
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

## 🧪 Тестирование

### 1. Проверка подключений:
```bash
python3 test_sheets_connection.py
```

### 2. Тест базы данных:
```bash
python3 reset_user.py list
```

### 3. Тест бота:
1. Найти тестового бота в Telegram
2. Отправить `/start`
3. Пройти полный flow

## 🚫 ЧТО НЕ ДЕЛАТЬ

- ❌ **НЕ использовать** продакшн BOT_TOKEN
- ❌ **НЕ использовать** продакшн DATABASE_URL  
- ❌ **НЕ использовать** продакшн Google Sheets
- ❌ **НЕ коммитить** credentials.json в git
- ❌ **НЕ коммитить** .env в git

## ✅ ЧТО ДЕЛАТЬ

- ✅ **Использовать** тестовые credentials
- ✅ **Тестировать** на тестовых данных
- ✅ **Коммитить** только код и документацию
- ✅ **Использовать** .env.example как шаблон

## 🔐 Доступы

### Что НУЖНО от владельца проекта:
1. **Email Service Account** (для добавления в Google Sheets)
2. **Структура таблиц** (схема данных)
3. **Документация** (ONBOARDING.md)

### Что НЕ НУЖНО:
1. **Приватные ключи** Service Account
2. **Пароли** базы данных
3. **Токены** продакшн бота
4. **Доступ** к продакшн данным

## 📞 Поддержка

Если нужен доступ к продакшн данным:
1. **Создать issue** в GitHub
2. **Описать задачу** и обоснование
3. **Получить разрешение** от владельца
4. **Получить временный доступ** (не постоянный!)

---

**Помните: безопасность превыше всего! 🛡️**
