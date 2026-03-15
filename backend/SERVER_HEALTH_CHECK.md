# 🔍 Проверка работоспособности сервера

## Быстрая проверка

### 1. Проверка через скрипт (рекомендуется)

```bash
cd backend
python scripts/check_server_health.py
```

Или с указанием URL:
```bash
python scripts/check_server_health.py --url http://localhost:8000
```

### 2. Ручная проверка

#### Проверка доступности сервера

```bash
# Проверка основного endpoint
curl http://localhost:8000/

# Проверка health check
curl http://localhost:8000/health

# Проверка документации
curl http://localhost:8000/docs
```

#### Проверка через браузер

- **Главная страница:** http://localhost:8000/
- **Health check:** http://localhost:8000/health
- **Swagger документация:** http://localhost:8000/docs
- **ReDoc документация:** http://localhost:8000/redoc

### 3. Проверка базы данных

```bash
# Через Python
cd backend
python -c "from app.core.database import engine; from sqlalchemy import text; conn = engine.connect(); print('DB OK' if conn.execute(text('SELECT 1')) else 'DB Error')"
```

Или через psql:
```bash
psql -h localhost -p 5437 -U user -d spa_db -c "SELECT 1;"
```

## Что проверяет скрипт

✅ **Конфигурация:**
- SECRET_KEY установлен и достаточно длинный
- DATABASE_URL настроен
- Окружение (development/production)

✅ **База данных:**
- Подключение к PostgreSQL
- Доступность базы данных

✅ **Endpoints:**
- GET / - основная страница
- GET /health - health check
- GET /docs - Swagger документация
- GET /api/v1/auth/me - API endpoint (может требовать авторизации)

## Типичные проблемы

### Сервер не запущен

**Решение:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### База данных недоступна

**Решение:**
```bash
# Запустите PostgreSQL через Docker
cd backend
docker-compose -f docker-compose.db.yml up -d

# Или через полный docker-compose
docker-compose up -d postgres
```

### Ошибка подключения к БД

**Проверьте:**
1. `.env` файл существует в папке `backend/`
2. `DATABASE_URL` правильный в `.env`
3. PostgreSQL запущен и доступен
4. База данных создана

**Создание базы данных:**
```bash
# Примените миграции
cd backend
alembic upgrade head
```

### SECRET_KEY не установлен

**Решение:**
1. Откройте `backend/.env`
2. Установите `SECRET_KEY` (минимум 32 символа)
3. Перезапустите сервер

## Ожидаемый результат

При успешной проверке вы увидите:

```
✓ SECRET_KEY установлен (длина: 64)
✓ DATABASE_URL установлен: ...@localhost:5437/spa_db
✓ Подключение к базе данных успешно
✓ GET / - Проверка доступности (200 OK)
✓ GET /health - Health check (200 OK)
✓ GET /docs - Swagger документация (200 OK)
✓ Все проверки пройдены успешно! ✅
```

## Автоматическая проверка

Можно добавить проверку в CI/CD или запускать периодически:

```bash
# Проверка каждые 5 минут (пример для cron)
*/5 * * * * cd /path/to/backend && python scripts/check_server_health.py
```

## Мониторинг

Для production рекомендуется использовать:
- **Health check endpoint:** `/health` - для мониторинга
- **Метрики:** можно добавить Prometheus endpoint
- **Логирование:** проверьте логи сервера

---

**Скрипт создан:** `backend/scripts/check_server_health.py`

