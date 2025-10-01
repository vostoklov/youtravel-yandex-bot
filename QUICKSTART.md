# 🚀 Быстрый старт - YouTravel Bot

## ✅ Что уже готово

- ✅ Telegram бот создан: `@youtravel_b2a_smm_bot`
- ✅ Google Sheets таблицы созданы и заполнены тестовыми данными
- ✅ Весь код бота написан и готов к деплою
- ✅ Service Account настроен

## 📋 Что осталось сделать (10 минут)

### 1️⃣ Создать PostgreSQL на Railway (2 минуты)

1. Открой: https://railway.app/new
2. Нажми "+ New Project"
3. Выбери "Deploy PostgreSQL"
4. Скопируй `DATABASE_URL` из Variables

### 2️⃣ Обновить .env файл (1 минута)

Открой файл `.env` и замени `DATABASE_URL`:

```env
DATABASE_URL=postgresql://postgres:password@host:port/railway
```

Все остальные переменные уже заполнены!

### 3️⃣ Загрузить проект на GitHub (3 минуты)

```bash
cd /home/claude/youtravel_bot
git init
git add .
git commit -m "Initial commit: YouTravel Bot"
git branch -M main
git remote add origin <your-github-repo>
git push -u origin main
```

### 4️⃣ Задеплоить на Railway (4 минуты)

1. В Railway нажми "+ New"
2. Выбери "GitHub Repo"  
3. Выбери свой репозиторий `youtravel_bot`
4. Railway автоматически обнаружит Python проект
5. Добавь переменные окружения (скопируй из `.env`):
   - `BOT_TOKEN`
   - `DATABASE_URL` (уже есть из шага 1)
   - `GOOGLE_SHEET_EMAILS_ID`
   - `GOOGLE_SHEET_PROMOS_ID`
   - `SUPPORT_USERNAME`
   - `ENVIRONMENT=production`
6. Для `credentials.json`: скопируй содержимое и вставь как `GOOGLE_CREDENTIALS_JSON`

### 5️⃣ Проверить (1 минута)

1. Открой Telegram → найди `@youtravel_b2a_smm_bot`
2. Отправь `/start`
3. Проверь что бот отвечает

## 🎉 Готово!

Бот запущен и работает!

## 📊 Ссылки на таблицы

- **Emails**: https://docs.google.com/spreadsheets/d/1xBFSvBBdKG27YAAfjMy6K0dEcFP4pQMUujpblK8tub0
- **Promos**: https://docs.google.com/spreadsheets/d/1RQvWCLGUocLTJqyBdwCRCEXnUkNmABhL7ng9-paLh6E

## 🐛 Если что-то не работает

1. **Проверь логи** в Railway Dashboard → Deployments → Logs
2. **Проверь переменные** в Railway → Variables
3. **Проверь БД** что `DATABASE_URL` правильный
4. **Напиши мне** @vostoklov

## 🔄 Обновление данных в таблицах

Чтобы добавить реальные email'ы и промокоды:

1. Открой таблицы по ссылкам выше
2. Замени тестовые данные на реальные
3. Бот автоматически начнёт использовать новые данные

## 📝 Примечания

- Бот работает 24/7 на Railway
- PostgreSQL бесплатен до 500MB
- Google Sheets работают в реальном времени
- Все промокоды помечаются как использованные автоматически
