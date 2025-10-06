# Чеклист деплоя бота на Railway

## ✅ Что уже сделано

1. ✅ Улучшено логирование в `sheets.py` (8 детальных шагов)
2. ✅ Добавлена поддержка файлов локально + JSON на Railway
3. ✅ Создан тест подключения `test_sheets_connection.py`
4. ✅ Создан helper script `prepare_railway_credentials.py`
5. ✅ JSON для Railway подготовлен и скопирован в буфер

## 🔧 Что нужно сделать

### Шаг 1: Дать доступ Service Account к Google Sheets

**Service Account Email**: `claude-by-ivan-bortnikov@probable-bebop-305708.iam.gserviceaccount.com`

#### Таблица 1: Emails
1. Открыть: https://docs.google.com/spreadsheets/d/1xBFSvBBdKG27YAAfjMy6K0dEcFP4pQMUujpblK8tub0
2. Кликнуть "Share" / "Поделиться" (правый верхний угол)
3. Вставить email: `claude-by-ivan-bortnikov@probable-bebop-305708.iam.gserviceaccount.com`
4. Роль: **Editor**
5. Нажать "Send"

#### Таблица 2: Promos
1. Открыть: https://docs.google.com/spreadsheets/d/1RQvWCLGUocLTJqyBdwCRCEXnUkNmABhL7ng9-paLh6E
2. Кликнуть "Share"
3. Вставить email: `claude-by-ivan-bortnikov@probable-bebop-305708.iam.gserviceaccount.com`
4. Роль: **Editor**
5. Нажать "Send"

### Шаг 2: Проверить локально

```bash
cd ~/Projects/youtravel_bot
python3 test_sheets_connection.py
```

**Ожидаемый результат**:
```
✅ Successfully connected to Google Sheets!
🎉 All tests passed!
```

### Шаг 3: Обновить GOOGLE_CREDENTIALS_JSON на Railway

JSON уже в буфере обмена (скопирован на предыдущем шаге).

1. Открыть Railway Dashboard: https://railway.app
2. Найти проект `youtravel-yandex-bot`
3. Перейти в **Variables** (вкладка слева)
4. Найти переменную `GOOGLE_CREDENTIALS_JSON`
5. Кликнуть "Edit"
6. **Вставить JSON из буфера** (Cmd+V)
7. Сохранить

**Важно**: Вставьте JSON **без дополнительных пробелов или переносов строк**!

### Шаг 4: Закоммитить изменения

```bash
cd ~/Projects/youtravel_bot
git add .
git commit -m "Fix: detailed Google Sheets logging + file/JSON support"
git push origin main
```

Railway автоматически задеплоит.

### Шаг 5: Проверить логи на Railway

1. Railway Dashboard → Deployments
2. Найти последний деплой
3. Открыть **Logs**

**Ожидаемое в логах**:
```
============================================================
Starting Google Sheets connection...
============================================================
Step 1: Reading GOOGLE_CREDENTIALS_JSON from environment
✓ Got credentials value, length: 2405 characters
Step 2: Determining if it's a file path or JSON string
  Detected as JSON string
...
✅ Successfully connected to Google Sheets!
🤖 Bot started
```

**Если ошибка 403**:
```
❌ Failed to open spreadsheet: PermissionError
```
→ Значит не дали доступ на Шаге 1. Проверьте email в Share настройках таблиц.

### Шаг 6: Удалить лишний сервис (опционально)

Если `mellow-kindness` крашится:
1. Railway Dashboard → Services
2. Найти `mellow-kindness`
3. Settings → Danger Zone → **Delete Service**

### Шаг 7: Протестировать бота

1. Открыть Telegram
2. Найти бота (по имени или токену)
3. Отправить `/start`

**Ожидаемый flow**:
```
👋 Привет! Это бот для регистрации в B2B Яндекс.Путешествий.
🎁 После регистрации вы получите промокод...
📝 Для начала, введите ваш email...
```

4. Ввести email из Google Sheets (таблица emails)
5. Проверить, что бот подтвердил email
6. Пройти регистрацию до конца
7. Получить промокод

## 📊 Структура Google Sheets

### Таблица Emails (Sheet1)
```
| Email                     |
|---------------------------|
| ivan@youtravel.me         |
| test@youtravel.me         |
```

### Таблица Promos (Sheet1)
```
| Promo Code       |
|------------------|
| YANDEX10OFF1     |
| YANDEX10OFF2     |
```

**Примечание**: Бот берет промокоды из колонки B (второй столбец), если у вас одна колонка - нужно либо:
- Добавить колонку A (заголовок), а промокоды в B
- Или изменить код в `sheets.py:67` с `col_values(2)` на `col_values(1)`

## 🐛 Траблшутинг

### Ошибка: `GOOGLE_CREDENTIALS_JSON not set`
→ Переменная окружения не задана на Railway

### Ошибка: `JSON parsing failed`
→ JSON некорректный. Запустите `prepare_railway_credentials.py` снова

### Ошибка: `PermissionError [403]`
→ Service account не имеет доступа. Вернитесь к Шагу 1

### Ошибка: `FileNotFoundError: credentials.json`
→ Локально: убедитесь что файл существует
→ Railway: должен быть JSON, а не путь к файлу

### Бот не отвечает
→ Проверьте `BOT_TOKEN` на Railway
→ Проверьте логи Railway (может быть ошибка подключения к БД)

### Ошибка подключения к БД
→ Проверьте `DATABASE_URL` на Railway
→ Убедитесь, что PostgreSQL сервис запущен

## 📝 Переменные окружения на Railway

```bash
BOT_TOKEN=8492820278:AAF7kKcWrgt3T3wK-STTUEjHvbuexE77apo
DATABASE_URL=postgresql://user:password@host:port/dbname
GOOGLE_SHEET_EMAILS_ID=1xBFSvBBdKG27YAAfjMy6K0dEcFP4pQMUujpblK8tub0
GOOGLE_SHEET_PROMOS_ID=1RQvWCLGUocLTJqyBdwCRCEXnUkNmABhL7ng9-paLh6E
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}  # <- Полный JSON!
ENVIRONMENT=production
LOG_LEVEL=INFO
SUPPORT_USERNAME=vostoklov
```

## 🎯 Цель проекта

- Собрать ≥100 регистраций B2B агентств
- Выдать промокоды -10% (кэп 10K₽)
- Интеграция YouTravel ↔ Яндекс.Путешествия

## 📞 Контакты

- **Репозиторий**: https://github.com/vostoklov/youtravel-yandex-bot
- **Railway Region**: europe-west4
- **Поддержка**: @vostoklov
- **Last commit**: f51b819

---

**Следующие шаги после деплоя**:
1. ✅ Протестировать полный flow с реальным email
2. ✅ Проверить, что промокод выдается
3. ✅ Убедиться, что данные сохраняются в PostgreSQL
4. 📢 Запустить промо кампанию
5. 📊 Мониторить метрики (регистрации, конверсия)


