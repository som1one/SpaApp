# Развёртывание PRIRODA SPA на сервере

Краткий гайд по деплою бэкенда, админки и (опционально) мобильного приложения.

---

## Требования на сервере

- **Docker** и **Docker Compose**
- Доступ по SSH
- Домен (опционально) для HTTPS через Nginx/Caddy

---

## 1. Клонирование и настройка окружения

```bash
git clone https://github.com/som1one/SpaApp.git
cd SpaApp
```

### 1.1 Переменные окружения бэкенда

```bash
cd backend
cp env.template .env
# Отредактируй .env под прод
nano .env
```

**Обязательно в `.env` для продакшена:**

| Переменная | Описание |
|------------|----------|
| `DATABASE_URL` | Подключение к PostgreSQL (в Docker будет переопределено на `postgres:5432`) |
| `SECRET_KEY` | Случайная строка ≥32 символов |
| `ADMIN_PANEL_BASE_URL` | URL админки, например `https://admin.твой-домен.ru` |
| `EMAIL_HOST`, `EMAIL_USER`, `EMAIL_PASSWORD`, `EMAIL_FROM` | SMTP для писем (инвайты, подтверждения) |
| `FCM_SERVER_KEY` | Server Key из Firebase Console (Cloud Messaging) — без него пуши не отправляются |
| `ENVIRONMENT=production` | Режим production |
| `DEBUG=False` | Отключить отладочный режим |
| `CORS_ORIGINS` | Домен админки и (если есть) API, через запятую |

Подробнее: **`backend/ENV_SETUP.md`**.

---

## 2. Запуск через Docker Compose

Compose-файл лежит в `backend/`, но собирает и backend, и admin из корня репозитория. Запуск **из корня проекта**:

```bash
cd /path/to/SpaApp
docker compose -f backend/docker-compose.yml up -d --build
```

Поднимаются:

- **postgres** — порт 5437 снаружи (внутри 5432)
- **redis** — порт 6379
- **backend** — порт 9003 (FastAPI)
- **admin** — порт 3001 (Vite dev-сервер)

### 2.1 Миграции и супер-админ

После первого запуска контейнеров:

```bash
cd backend

# Миграции (локально, к БД в Docker)
export DATABASE_URL=postgresql://user:password@localhost:5437/spa_db
pip install -r requirements.txt
alembic upgrade head

# Создать супер-админа (логин в админку)
python scripts/create_super_admin.py
```

Либо выполнить миграции **внутри контейнера**:

```bash
docker exec -it spa_backend alembic upgrade head
docker exec -it spa_backend python scripts/create_super_admin.py
```

(В контейнере `DATABASE_URL` уже указывает на `postgres:5432`.)

---

## 3. Доступ к сервисам

- **Админка:** `http://IP_СЕРВЕРА:3001`  
  Логин — email/пароль супер-админа из шага 2.
- **API бэкенда:** `http://IP_СЕРВЕРА:9003`  
  Префикс API: `http://IP_СЕРВЕРА:9003/api/v1`

Для продакшена лучше отдать оба сервиса через **обратный прокси** (Nginx/Caddy) с HTTPS и задать в `.env`:

- `ADMIN_PANEL_BASE_URL=https://admin.твой-домен.ru`
- `CORS_ORIGINS=https://admin.твой-домен.ru,https://твой-домен.ru`

---

## 4. Админка: указание API при сборке/запуске

Сейчас админка в Docker запускается как Vite dev-сервер с переменной:

`VITE_API_BASE_URL=http://backend:8000/api/v1`

Это работает, когда браузер открывает админку по тому же хосту (порт 3001), а запросы к API проксируются или бэкенд доступен по тому же домену. Если админка открывается по домену, а API по другому домену/порту, при сборке статики нужно передать публичный URL API, например:

```bash
# Пример для production-сборки админки (если будет отдельный Dockerfile с build)
VITE_API_BASE_URL=https://api.твой-домен.ru/api/v1 npm run build
```

В текущем `admin/Dockerfile` используется `npm run dev`; переменная задаётся в `docker-compose.yml` для контейнера. Для продакшена с отдельным доменом настрой в `backend/docker-compose.yml`:

```yaml
admin:
  environment:
    VITE_API_BASE_URL: https://api.твой-домен.ru/api/v1
```

и пересобери образ админки.

---

## 5. Nginx (пример для HTTPS)

Установка Nginx на хост и пример конфига:

```nginx
# /etc/nginx/sites-available/spa-app

# Админка
server {
    listen 80;
    server_name admin.твой-домен.ru;
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# API бэкенда
server {
    listen 80;
    server_name api.твой-домен.ru;
    location / {
        proxy_pass http://127.0.0.1:9003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Включи сайт и получи сертификаты (Let's Encrypt):

```bash
sudo ln -s /etc/nginx/sites-available/spa-app /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d admin.твой-домен.ru -d api.твой-домен.ru
```

После этого в `.env` укажи `ADMIN_PANEL_BASE_URL=https://admin.твой-домен.ru` и перезапусти контейнеры.

---

## 6. Обновление деплоя

```bash
cd /path/to/SpaApp
git pull origin main
docker compose -f backend/docker-compose.yml up -d --build
# При изменении схемы БД:
docker exec -it spa_backend alembic upgrade head
```

---

## 7. Полезные команды

```bash
# Логи бэкенда
docker logs -f spa_backend

# Логи админки
docker logs -f spa_admin

# Остановить всё
docker compose -f backend/docker-compose.yml down

# Остановить с удалением данных (БД, Redis)
docker compose -f backend/docker-compose.yml down -v
```

---

## 8. Мобильное приложение (Flutter)

Сборка под магазины делается локально или в CI (Codemagic, GitHub Actions и т.п.), не на этом сервере. Сервер нужен только для:

- API бэкенда (порт 9003 или за Nginx)
- Админки (порт 3001 или за Nginx)

В приложении укажи базовый URL API (например `https://api.твой-домен.ru/api/v1`) там, где задаётся `ApiService` / `baseUrl`. Деплой самого сервера по этому гайду этого не заменяет — только бэкенд и админка.

---

Итог: на сервере клонируешь репо, настраиваешь `backend/.env`, поднимаешь стек через `docker compose -f backend/docker-compose.yml`, прогоняешь миграции и создаёшь супер-админа. Детали по переменным — в **`backend/ENV_SETUP.md`** и **`spa/docs/FIREBASE_CREDENTIALS.md`** (для FCM).
