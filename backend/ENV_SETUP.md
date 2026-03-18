# Настройка переменных окружения

Файл `.env` создан в папке `backend/`. Отредактируйте его и заполните следующие переменные:

## Обязательные переменные

### 1. База данных
```env
DATABASE_URL=postgresql://user:password@localhost:5432/spa_db
```
**Что изменить:**
- `user` - имя пользователя PostgreSQL
- `password` - пароль пользователя
- `spa_db` - название базы данных

**Для локальной разработки с Docker:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/spa_db
```
(используются значения из `docker-compose.yml`)

### 2. Безопасность
```env
SECRET_KEY=your-secret-key-change-in-production-minimum-32-characters-long
```
**ВАЖНО:** Сгенерируйте случайный секретный ключ минимум 32 символа!

**Способы генерации:**
```python
# Python
import secrets
print(secrets.token_urlsafe(32))

# Или онлайн генератор:
# https://djecrety.ir/
```

### 3. Email настройки (для отправки кодов подтверждения)

#### Gmail:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-here
EMAIL_FROM=noreply@spa-app.com
EMAIL_USE_TLS=True
```

**Как получить пароль приложения для Gmail:**
1. Включите двухфакторную аутентификацию
2. Перейдите в https://myaccount.google.com/apppasswords
3. Создайте пароль приложения для "Почта"
4. Используйте этот пароль в `EMAIL_PASSWORD`

#### Yandex:
```env
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USER=your-email@yandex.ru
EMAIL_PASSWORD=your-password
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
```

#### Mail.ru:
```env
EMAIL_HOST=smtp.mail.ru
EMAIL_PORT=465
EMAIL_USER=your-email@mail.ru
EMAIL_PASSWORD=your-password
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
```

## Опциональные переменные

### Redis (для кеширования и сессий)
```env
REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=False
```
Поставьте `True` если используете Redis.

### CORS Origins
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,*
```
Добавьте домены вашего Flutter приложения.

### Настройки бронирований
```env
MIN_BOOKING_ADVANCE_HOURS=2      # Минимум за сколько часов можно забронировать
MAX_BOOKING_ADVANCE_DAYS=30      # Максимум на сколько дней вперед
CANCELLATION_HOURS_BEFORE=24      # За сколько часов можно отменить
```

### Firebase Cloud Messaging (push-уведомления)

Чтобы админка могла отправлять push-рассылки на мобильные устройства, настройте **FCM v1** (рекомендуется) или Legacy.

**Вариант 1 — FCM HTTP v1 API (рекомендуется):**

1. [Firebase Console](https://console.firebase.google.com/) → ваш проект → **Project settings** → вкладка **General** → скопируйте **Project ID**.
2. Вкладка **Service accounts** → **Generate new private key** — скачайте JSON ключа сервисного аккаунта.
3. В `.env` задайте один из вариантов:

   **Через путь к файлу:**
   ```env
   FCM_PROJECT_ID=ваш-project-id
   GOOGLE_APPLICATION_CREDENTIALS=/абсолютный/путь/к/ключу.json
   ```

   **Через JSON строкой (удобно для Docker):**
   ```env
   FCM_PROJECT_ID=ваш-project-id
   FCM_CREDENTIALS_JSON={"type":"service_account","project_id":"...",...}
   ```

**Вариант 2 — Legacy (если включён Cloud Messaging API (Legacy)):**

```env
FCM_SERVER_KEY=ваш-server-key-из-firebase-console
```

Server key: Firebase Console → **Project settings** → вкладка **Cloud Messaging** → блок **Cloud Messaging API (Legacy)**.

Без настроенного FCM (v1 или Legacy) рассылки из раздела «Рассылки» не будут отправляться. Подробнее: **`spa/docs/FIREBASE_SETUP.md`**, **`spa/docs/FIREBASE_CREDENTIALS.md`**.

## Проверка настроек

После заполнения `.env` файла, запустите:

```bash
cd backend
python -c "from app.core.config import settings; print('✅ Config loaded successfully')"
```

Если ошибок нет - всё готово!

## Безопасность

⚠️ **НИКОГДА не коммитьте `.env` файл в Git!**

Файл уже добавлен в `.gitignore`. Для других разработчиков используйте `env.template`.

## Примеры готовых конфигураций

### Локальная разработка
```env
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/spa_db
SECRET_KEY=dev-secret-key-not-for-production
CORS_ORIGINS=*
```

### Продакшн
```env
DEBUG=False
DATABASE_URL=postgresql://user:password@production-db:5432/spa_db
SECRET_KEY=super-secret-production-key-32-chars-minimum
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

