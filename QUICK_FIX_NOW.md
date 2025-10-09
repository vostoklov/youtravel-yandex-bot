# ⚡ ЧТО ДЕЛАТЬ ПРЯМО СЕЙЧАС

## 🔴 СРОЧНО: 3 шага для исправления

### ШАГ 1: Анализ (1 минута)

**Самый простой способ - через Telegram бота:**

Откройте бота и отправьте:

```
/admin_check_email nzamaldinova@gmail.com
```

Это покажет все записи для этого email и выявит дубликаты.

**Альтернатива через терминал (если нужна полная картина):**

```bash
cd /Users/ivanbortnikov/Projects/youtravel_bot
railway run python analyze_promo_issue.py
```

---

### ШАГ 2: Исправление БД (5 минут)

**Вариант А - Автоматический (рекомендуется):**

```bash
railway run python fix_nzamaldinova_duplicates.py
```

**Вариант Б - Ручной (если нужен контроль):**

1. Зайдите в Railway Dashboard
2. Откройте PostgreSQL console
3. Выполните:

```sql
-- Смотрим, что есть
SELECT user_id, email, promo_code, created_at 
FROM users 
WHERE email = 'nzamaldinova@gmail.com';

-- Удаляем дубликаты (оставляем только запись с ИНН)
DELETE FROM users 
WHERE email = 'nzamaldinova@gmail.com' 
AND inn IS NULL;
```

---

### ШАГ 3: Google Sheets (10 минут)

#### 3.1 Таблица "Registered Users"

Ссылка: https://docs.google.com/spreadsheets/d/1xBFSvBBdKG27YAAfjMy6K0dEcFP4pQMUujpblK8tub0/edit#gid=0

**Найти строки:**
- nzamaldinova@gmail.com с пустым ИНН → УДАЛИТЬ
- nzamaldinova@gmail.com без промокода → УДАЛИТЬ
- nzamaldinova@gmail.com с промокодом YOUTRAVELCME4IAZJU6 → УДАЛИТЬ
- nzamaldinova@gmail.com с промокодом YOUTRAVELOZ3DZVJ7NQ → УДАЛИТЬ
- nzamaldinova@gmail.com с промокодом YOUTRAVELJFUHCYBOZT → УДАЛИТЬ

**Оставить ТОЛЬКО:**
```
Email: nzamaldinova@gmail.com
ИНН: 7718718506
Промокод: YOUTRAVELGDLWN7IKDV
Дата: 09.10.2025 11:48
```

#### 3.2 Таблица "Promos"

Для КАЖДОГО промокода ниже изменить:
- Статус: `used` → `available`
- Дата выдачи: ОЧИСТИТЬ (пустая ячейка)

**Список промокодов для восстановления:**

1. ☑️ YOUTRAVELCME4IAZJU6
2. ☑️ YOUTRAVELOZ3DZVJ7NQ
3. ☑️ YOUTRAVELJFUHCYBOZT
4. ☑️ YOUTRAVELBRGJJ77O22
5. ☑️ YOUTRAVELOB4VD2YBL7
6. ☑️ YOUTRAVELBVHEW48XL7
7. ☑️ YOUTRAVELPXP5N77LH7
8. ☑️ YOUTRAVELLBXZL6T3G3

---

## ✅ ПРОВЕРКА (2 минуты)

После всех исправлений откройте Telegram и отправьте боту:

```
/admin_stats
```

Должно показать:
- ✅ Всего: 2 пользователя
- ✅ Завершили: 1
- ✅ Выдано промокодов: 1
- ✅ Доступно: ~142 (если было 150 промокодов)

Затем:

```
/admin_users
```

Должна быть только ОДНА запись для nzamaldinova@gmail.com с промокодом YOUTRAVELGDLWN7IKDV.

---

## 💬 СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЮ

После исправления отправьте:

```
Здравствуйте!

Во время регистрации произошла техническая ошибка, и система выдала несколько промокодов. 

✅ Ваш действующий промокод: YOUTRAVELGDLWN7IKDV

Он уже активен и готов к использованию на travel.yandex.ru

Промокод даёт −10% (до 10 000 ₽) на бронирования до 10 ноября 2025.

Приносим извинения за неудобства 🙏
```

---

## 📊 ИТОГО

**Время:** ~15-20 минут  
**Результат:** Проблема полностью исправлена  
**Профилактика:** Уже исправлено в коде (commit da43507)

---

## 🆘 ЕСЛИ ЧТО-ТО ПОШЛО НЕ ТАК

1. Проверьте логи:
   ```bash
   railway logs --lines 100
   ```

2. Запустите анализ заново:
   ```bash
   railway run python analyze_promo_issue.py
   ```

3. Полная документация: `EMERGENCY_FIX_GUIDE.md`

