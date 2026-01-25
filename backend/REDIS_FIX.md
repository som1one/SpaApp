# 🔧 Исправление проблемы с Redis

## Проблема

Redis контейнер пытается подключиться к внешнему мастеру (121.204.162.239:20886) и постоянно получает ошибки "Connection refused". Это происходит потому, что в volume Redis сохранилась старая конфигурация, где Redis был настроен как реплика.

## Решение

### Вариант 1: Пересоздание Redis контейнера (рекомендуется)

```bash
# Остановите Redis
docker-compose stop redis

# Удалите контейнер и volume
docker-compose rm -f redis
docker volume rm backend_redis_data

# Запустите Redis заново
docker-compose up -d redis
```

### Вариант 2: Полная перезагрузка всех сервисов

```bash
# Остановите все сервисы
docker-compose down

# Удалите volume Redis (если нужно)
docker volume rm backend_redis_data

# Запустите заново
docker-compose up -d
```

### Вариант 3: Ручная очистка конфигурации Redis

```bash
# Войдите в контейнер Redis
docker exec -it spa_redis sh

# Внутри контейнера выполните:
redis-cli
CONFIG SET replicaof ""
CONFIG REWRITE
exit
exit

# Перезапустите контейнер
docker-compose restart redis
```

## Проверка

После исправления проверьте логи:

```bash
docker-compose logs redis
```

Вы должны увидеть:
```
* Ready to accept connections
```

И НЕ должно быть:
```
* Connecting to MASTER 121.204.162.239:20886
* Error condition on socket for SYNC
```

## Что было исправлено

1. ✅ Добавлена команда запуска Redis: `redis-server --appendonly yes`
   - Это гарантирует, что Redis запускается как standalone сервер
   - `--appendonly yes` включает персистентность данных

2. ✅ Добавлен `restart: unless-stopped` для автоматического перезапуска

## Профилактика

Чтобы избежать этой проблемы в будущем:

1. **Не используйте Redis как реплику** для локальной разработки
2. **Очищайте volumes** при изменении конфигурации Redis
3. **Используйте отдельные volumes** для development и production

## Дополнительная информация

- Redis должен работать как standalone сервер для локальной разработки
- Репликация нужна только для production с высокой нагрузкой
- В вашем случае Redis используется опционально (`REDIS_ENABLED=False` по умолчанию)

---

**После исправления Redis будет работать как standalone сервер без попыток синхронизации с внешним мастером.**

