# 🚨 СРОЧНОЕ ИСПРАВЛЕНИЕ: Множественная выдача промокодов

## Что произошло

**Пользователь:** nzamaldinova@gmail.com (ID: 2200122)  
**Проблема:** Получил 4 промокода вместо 1  
**Время:** 09.10.2025, 11:46 - 11:51 (5 минут)  
**Масштаб:** 10 промокодов помечены как "used" в Google Sheets

### Список пострадавших промокодов:

1. ✅ **YOUTRAVELGDLWN7IKDV** - первый выданный, оставляем пользователю
2. ❌ YOUTRAVELBRGJJ77O22 - не понятно кому выдан
3. ❌ YOUTRAVELOB4VD2YBL7 - не понятно кому выдан  
4. ❌ YOUTRAVELBVHEW48XL7 - не понятно кому выдан
5. ❌ YOUTRAVELPXP5N77LH7 - не понятно кому выдан
6. ❌ YOUTRAVELLBXZL6T3G3 - не понятно кому выдан
7. ❌ YOUTRAVELCME4IAZJU6 - выдан nzamaldinova@gmail.com (дубликат)
8. ❌ YOUTRAVELOZ3DZVJ7NQ - выдан nzamaldinova@gmail.com (дубликат)
9. ❌ YOUTRAVELJFUHCYBOZT - выдан nzamaldinova@gmail.com (дубликат)
10. ℹ️ YOUTRAVELTEST1 - тестовый промокод (07.10.2025)

## Причина проблемы

### До исправления:
1. Пользователь мог несколько раз нажать кнопку "✅ Да, всё верно"
2. `callback.answer()` вызывался слишком поздно → таймауты
3. Не было защиты от повторной регистрации
4. При ошибке использовался `edit_text` вместо `answer`

### После исправления (da43507):
1. ✅ `callback.answer()` вызывается сразу
2. ✅ Проверка "уже завершил регистрацию"
3. ✅ Fallback через `answer()` вместо `edit_text()`
4. ✅ Удаление старого сообщения с кнопками

## План исправления

### ⚡ ЭТАП 1: Анализ базы данных (ОБЯЗАТЕЛЬНО!)

Запустите скрипт анализа через Railway CLI:

```bash
railway run python analyze_promo_issue.py
```

Это покажет:
- Сколько записей в БД для nzamaldinova@gmail.com
- Какие промокоды реально выданы
- Есть ли другие пострадавшие пользователи

### 🔧 ЭТАП 2: Очистка базы данных

**Опция А: Автоматическая очистка (рекомендуется)**

```bash
railway run python fix_nzamaldinova_duplicates.py
```

Скрипт:
- Найдет все записи для nzamaldinova@gmail.com
- Оставит только первую (с ИНН и первым промокодом)
- Удалит остальные
- Выведет список промокодов для восстановления

**Опция Б: Ручная очистка через Railway shell**

```bash
railway run bash
psql $DATABASE_URL
```

```sql
-- 1. Проверяем записи
SELECT user_id, email, inn, promo_code, created_at 
FROM users 
WHERE email = 'nzamaldinova@gmail.com' 
ORDER BY created_at;

-- 2. Удаляем дубликаты (оставляем только первую запись)
DELETE FROM users 
WHERE email = 'nzamaldinova@gmail.com' 
AND user_id != (
    SELECT user_id 
    FROM users 
    WHERE email = 'nzamaldinova@gmail.com' 
    AND inn IS NOT NULL 
    ORDER BY created_at 
    LIMIT 1
);

-- 3. Проверяем результат
SELECT * FROM users WHERE email = 'nzamaldinova@gmail.com';
```

### 📊 ЭТАП 3: Исправление Google Sheets

#### Таблица "Registered Users"

1. Откройте: https://docs.google.com/spreadsheets/d/1xBFSvBBdKG27YAAfjMy6K0dEcFP4pQMUujpblK8tub0/edit#gid=0
2. Найдите строки с `nzamaldinova@gmail.com`
3. **Удалите дубликаты**, оставьте только:
   ```
   Email: nzamaldinova@gmail.com
   ИНН: 7718718506
   Промокод: YOUTRAVELGDLWN7IKDV
   Дата: 09.10.2025 11:48
   ```

#### Таблица "Promos"

Откройте лист "Promos" и для каждого промокода из списка ниже:

**Промокоды для восстановления:**

1. YOUTRAVELCME4IAZJU6
2. YOUTRAVELOZ3DZVJ7NQ
3. YOUTRAVELJFUHCYBOZT
4. YOUTRAVELBRGJJ77O22
5. YOUTRAVELOB4VD2YBL7
6. YOUTRAVELBVHEW48XL7
7. YOUTRAVELPXP5N77LH7
8. YOUTRAVELLBXZL6T3G3

**Для каждого:**
- Колонка "Статус": измените `used` → `available`
- Колонка "Дата выдачи": очистите ячейку (должна быть пустой)

### 💬 ЭТАП 4: Сообщение пользователю

Отправьте пользователю через бот или напрямую:

```
Здравствуйте!

Во время регистрации произошла техническая ошибка, и система выдала несколько промокодов. 

✅ Ваш действующий промокод: YOUTRAVELGDLWN7IKDV

Он уже активен и готов к использованию. Промокод даёт −10% (до 10 000 ₽) на бронирования в Яндекс.Путешествиях до 10 ноября 2025.

Приносим извинения за неудобства. Если у вас возникнут вопросы, напишите @maria_youtravel
```

### ✅ ЭТАП 5: Проверка

После всех исправлений проверьте через бота:

1. `/admin_stats` - должно показать корректное количество доступных промокодов
2. `/admin_users` - должна быть только одна запись для nzamaldinova@gmail.com
3. Попробуйте зарегистрировать тестового пользователя - убедитесь, что нельзя получить несколько промокодов

## Команды для быстрого доступа

### Анализ проблемы
```bash
railway run python analyze_promo_issue.py
```

### Исправление дубликатов
```bash
railway run python fix_nzamaldinova_duplicates.py
```

### Проверка статистики
В Telegram боте:
```
/admin_stats
/admin_users
```

## Мониторинг

### Логи Railway
```bash
railway logs --lines 100
```

### Что искать в логах:
- ✅ `User already completed registration` - защита работает
- ❌ `query is too old` - таймауты (не должно больше быть)
- ❌ Множественные `completed registration with promo` для одного user_id

## Предотвращение в будущем

### ✅ Уже исправлено в коде (da43507):
1. Немедленный `callback.answer()`
2. Проверка завершенной регистрации
3. Правильный fallback без дубликатов
4. Try-catch для всех уведомлений

### 🔍 Дополнительная защита (TODO):
1. Rate limiting на уровне пользователя
2. Блокировка кнопки после первого клика
3. Транзакции при выдаче промокода
4. Логирование всех попыток получения промокода

## Контрольный список

- [ ] Запущен `analyze_promo_issue.py`
- [ ] Проанализированы результаты
- [ ] Запущен `fix_nzamaldinova_duplicates.py` или выполнена ручная очистка БД
- [ ] Удалены дубликаты в Google Sheets → "Registered Users"
- [ ] Восстановлены промокоды в Google Sheets → "Promos"
- [ ] Отправлено сообщение пользователю
- [ ] Проверена работа через `/admin_stats` и `/admin_users`
- [ ] Проведена тестовая регистрация
- [ ] Проверены логи Railway

## Вопросы и помощь

Если что-то пошло не так:
1. Проверьте логи: `railway logs --lines 100`
2. Проверьте БД: `railway run python analyze_promo_issue.py`
3. Свяжитесь с @maria_youtravel для координации с пользователем

