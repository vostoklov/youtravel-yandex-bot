# Гайд по тестированию /reset

## 🔍 Проблема
Команда `/reset` возвращает ошибку без деталей.

## ✅ Что сделано
1. Добавлено детальное логирование в `/reset`
2. Теперь бот показывает тип ошибки пользователю
3. Полный traceback пишется в логи

## 🧪 Как протестировать

### Вариант 1: Через бота (рекомендуется)

1. **Отправить `/reset` боту СЕЙЧАС**
2. **Посмотреть ответ** - теперь должен показывать тип ошибки
3. **Посмотреть логи:**
   ```bash
   cd ~/Projects/youtravel_bot
   railway logs --lines 100
   ```
   
   Найти строки:
   ```
   User XXXXX requested reset
   ❌ Error resetting user
   ```

### Вариант 2: Через SQL на Railway

1. Railway Dashboard → PostgreSQL service
2. Data tab → Query
3. Выполнить:
   ```sql
   -- Посмотреть пользователей
   SELECT telegram_id, username, email, inn, promo_code 
   FROM users 
   ORDER BY created_at DESC;
   
   -- Удалить свою регистрацию (замените YOUR_ID на ваш telegram_id из запроса выше)
   DELETE FROM users WHERE telegram_id = YOUR_TELEGRAM_ID;
   ```

4. После этого `/start` в боте для новой регистрации

## 🎯 Если снова ошибка

Попробуйте `/reset` и сразу выполните:
```bash
cd ~/Projects/youtravel_bot
railway logs --lines 200 | grep -A 20 "reset"
```

Или покажите мне:
1. Точное сообщение от бота
2. Вывод команды выше

## 📋 Возможные ошибки

### `AttributeError: 'NoneType' object has no attribute 'pool'`
**Причина**: База данных не подключена
**Решение**: Проверить `DATABASE_URL` на Railway

### `asyncpg.exceptions.UndefinedTableError: relation "users" does not exist`
**Причина**: Таблица не создана
**Решение**: Перезапустить бот (Railway restart)

### `asyncpg.exceptions.InsufficientPrivilegeError`
**Причина**: Недостаточно прав для DELETE
**Решение**: Проверить права пользователя БД

## 🔧 Быстрый фикс

Если `/reset` не работает вообще, можно просто:
1. Использовать SQL (см. Вариант 2 выше)
2. Или временно закомментировать проверку в `/start`:
   ```python
   # if user and user.get('completed_at'):
   #     # ... вернуть старый промокод
   #     return
   ```
   Тогда можно просто начать `/start` заново

