# Backend API для SPA приложения

## Выбранный стек: FastAPI

## Быстрый старт

### 1. Установка зависимостей

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/spa_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-password
```

### 3. Запуск базы данных

```bash
docker-compose up -d
```

### 4. Применение миграций

```bash
alembic upgrade head
```

### 5. Запуск сервера

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Документация API

После запуска доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Структура проекта

См. `BACKEND_STRUCTURE_OPTIONS.md` для детального описания структуры.

## Основные эндпоинты (Auth)

- `POST /api/v1/auth/register` - Регистрация (возвращает код в ответе)
- `POST /api/v1/auth/login` - Вход (возвращает JWT токены)
- `POST /api/v1/auth/verify-email` - Подтверждение email
- `POST /api/v1/auth/resend-code` - Повторная отправка кода
- `GET /api/v1/auth/me` - Профиль текущего пользователя

### Особенность верификации:
При регистрации и resend-code бэкенд:
1. Генерирует код
2. Возвращает код в ответе клиенту
3. Параллельно отправляет код на email через BackgroundTasks

## Разработка

### Добавление новой миграции

```bash
alembic revision --autogenerate -m "Описание изменений"
alembic upgrade head
```

### Запуск тестов

```bash
pytest
```

### Форматирование кода

```bash
black .
isort .
```

