"""
Скрипт для инициализации необходимых стартовых данных в базе:
- создание супер-админа для админ-панели
- заполнение уровней лояльности, бонусов, категорий и услуг

Ожидания:
- миграции БД уже применены (alembic upgrade head)
- в .env заданы SUPER_ADMIN_EMAIL и SUPER_ADMIN_PASSWORD

Запуск локально:
    cd backend
    python -m scripts.init_default_data

Запуск в Docker (через docker-compose):
    docker-compose exec backend python -m scripts.init_default_data
"""

import sys
from pathlib import Path


# Добавляем корень backend в PYTHONPATH, как в других скриптах
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from scripts.seed_data import main as seed_data_main  # type: ignore
from scripts.create_super_admin import main as create_super_admin_main  # type: ignore


def main() -> None:
    print("=" * 60)
    print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ: СУПЕР-АДМИН + СТАРТОВЫЕ ДАННЫЕ")
    print("=" * 60)

    try:
        # 1. Создание супер-админа
        print("\n[1/2] Создание супер-админа...")
        create_super_admin_main()

        # 2. Заполнение стартовых данных (лояльность, категории, услуги)
        print("\n[2/2] Заполнение стартовых данных...")
        seed_data_main()

        print("\n" + "=" * 60)
        print("✓ ГОТОВО: супер-админ и стартовые данные созданы/обновлены.")
        print("=" * 60)
    except Exception as exc:  # noqa: BLE001
        print("\n✗ ОШИБКА при инициализации данных:")
        print(exc)
        raise


if __name__ == "__main__":
    main()


