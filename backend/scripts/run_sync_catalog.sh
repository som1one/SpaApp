#!/bin/bash
# Скрипт для запуска синхронизации каталога YClients
# Использование: ./run_sync_catalog.sh

echo "=========================================="
echo "🔄 Синхронизация каталога YClients"
echo "=========================================="
echo ""

# Активируем виртуальное окружение если есть
if [ -d ".venv" ]; then
    echo "📦 Активация виртуального окружения..."
    source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
fi

# Запускаем синхронизацию
echo "🚀 Запуск синхронизации..."
python scripts/sync_yclients_catalog.py

echo ""
echo "✅ Готово!"
echo ""
echo "💡 Проверьте результаты выше"
echo "💡 Для проверки в БД выполните:"
echo "   SELECT COUNT(*) FROM services WHERE yclients_service_id IS NOT NULL;"
echo "   SELECT COUNT(*) FROM staff WHERE yclients_staff_id IS NOT NULL;"

