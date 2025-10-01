# Фикс Google Sheets доступа

## Проблема
```
APIError: [403]: The caller does not have permission
Service account: claude-by-ivan-bortnikov@probable-bebop-305708.iam.gserviceaccount.com
```

## Решение

### 1. Дать доступ Service Account к таблицам

#### Таблица с emails (ID: 1xBFSvBBdKG27YAAfjMy6K0dEcFP4pQMUujpblK8tub0)
1. Открыть: https://docs.google.com/spreadsheets/d/1xBFSvBBdKG27YAAfjMy6K0dEcFP4pQMUujpblK8tub0
2. Нажать кнопку "Share" / "Поделиться" (правый верхний угол)
3. Добавить email: `claude-by-ivan-bortnikov@probable-bebop-305708.iam.gserviceaccount.com`
4. Выбрать роль: **Editor** (или минимум Viewer для чтения)
5. Нажать "Send" / "Отправить"

#### Таблица с промокодами (ID: 1RQvWCLGUocLTJqyBdwCRCEXnUkNmABhL7ng9-paLh6E)
1. Открыть: https://docs.google.com/spreadsheets/d/1RQvWCLGUocLTJqyBdwCRCEXnUkNmABhL7ng9-paLh6E
2. Нажать кнопку "Share" / "Поделиться"
3. Добавить email: `claude-by-ivan-bortnikov@probable-bebop-305708.iam.gserviceaccount.com`
4. Выбрать роль: **Editor**
5. Нажать "Send" / "Отправить"

### 2. Проверить доступ локально

После добавления доступа запустите тест:
```bash
cd ~/Projects/youtravel_bot
python3 test_sheets_connection.py
```

Должно быть:
```
✅ Successfully connected to Google Sheets!
```

### 3. Настройка Railway

#### Переменные окружения (уже настроены):
- ✅ `BOT_TOKEN`
- ✅ `DATABASE_URL`
- ✅ `GOOGLE_SHEET_EMAILS_ID`
- ✅ `GOOGLE_SHEET_PROMOS_ID`
- ⚠️ `GOOGLE_CREDENTIALS_JSON` - должен содержать **полный JSON**, а не путь к файлу

#### Как получить JSON для Railway:
```bash
cat ~/Projects/youtravel_bot/credentials.json | jq -c
```

Или просто скопировать содержимое файла `credentials.json` **целиком** в переменную окружения `GOOGLE_CREDENTIALS_JSON` на Railway (без переносов строк, одной строкой).

### 4. Деплой на Railway

После исправления прав доступа:
```bash
cd ~/Projects/youtravel_bot
git add sheets.py test_sheets_connection.py
git commit -m "Fix: detailed Google Sheets logging and file/JSON support"
git push origin main
```

Railway автоматически задеплоит обновление.

## Улучшения в коде

### sheets.py
✅ Детальное пошаговое логирование (8 шагов)
✅ Поддержка путей к файлам локально + JSON строк на Railway
✅ Проверка обязательных полей в credentials
✅ Детальные ошибки с указанием типа и позиции

### Пример успешного подключения:
```
============================================================
Starting Google Sheets connection...
============================================================
Step 1: Reading GOOGLE_CREDENTIALS_JSON from environment
✓ Got credentials value, length: 16 characters
Step 2: Determining if it's a file path or JSON string
  Looks like a file path: credentials.json
  Reading credentials from file: credentials.json
✓ File read successfully, length: 2405 characters
Step 3: Parsing JSON credentials
✓ JSON parsed successfully
Step 4: Validating credentials structure
✓ All required fields present
  Service account email: claude-by-ivan-bortnikov@probable-bebop-305708.iam.gserviceaccount.com
  Project ID: probable-bebop-305708
Step 5: Creating ServiceAccountCredentials
✓ Service account credentials created
Step 6: Authorizing gspread client
✓ Gspread client authorized
Step 7: Opening spreadsheet with ID: 1xBFSvBBdKG27YAAfjMy6K0dEcFP4pQMUujpblK8tub0
✓ Spreadsheet opened: YouTravel Emails
Step 8: Getting first worksheet
✓ Worksheet loaded: Sheet1
============================================================
✅ Successfully connected to Google Sheets!
============================================================
```

## Тестирование

После фикса запустите:
```bash
python3 test_sheets_connection.py
```

Проверьте логи Railway:
```bash
# В Railway web console -> Deployments -> Logs
```

## Структура Google Sheets

### Таблица Emails (Sheet1)
```
| Email                  |
|------------------------|
| user1@youtravel.me     |
| user2@youtravel.me     |
| ...                    |
```

### Таблица Promos (Sheet1)
```
| Promo Code    | Status     |
|---------------|------------|
| YANDEX10OFF1  | available  |
| YANDEX10OFF2  | available  |
| ...           |            |
```

## Удаление лишнего сервиса mellow-kindness

В Railway console:
1. Settings сервиса mellow-kindness
2. Danger Zone -> Delete Service

## Контакты
- Репозиторий: https://github.com/vostoklov/youtravel-yandex-bot
- Railway: europe-west4
- Service Account: claude-by-ivan-bortnikov@probable-bebop-305708.iam.gserviceaccount.com

