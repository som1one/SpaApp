"""
Скрипт для заполнения базы данных стартовыми данными:
- Уровни лояльности
- Категории меню
- Услуги

Запуск: python -m scripts.seed_data
"""
import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.base import BaseModel
from app.models.loyalty import LoyaltyLevel as LoyaltyLevelModel, LoyaltyBonus as LoyaltyBonusModel
from app.models.service import Service, ServiceCategory


def create_loyalty_levels(db: Session):
    """Создать стандартные уровни лояльности с именами 0–4.

    Если уровни уже есть – обновляем их параметры, чтобы конфиг всегда был
    в консистентном состоянии.
    """
    print("Создание уровней лояльности...")

    levels_data = [
        {
            "name": "0",
            "min_bonuses": 0,
            "cashback_percent": 1,
            "color_start": "#5A7C4A",  # primary
            "color_end": "#7A9C6A",    # primaryLight
            "icon": "eco",
            "order_index": 0,
            "is_active": True,
        },
        {
            "name": "1",
            "min_bonuses": 30000,
            "cashback_percent": 3,
            "color_start": "#5A7C4A",
            "color_end": "#7A9C6A",
            "icon": "eco",
            "order_index": 1,
            "is_active": True,
        },
        {
            "name": "2",
            "min_bonuses": 100000,
            "cashback_percent": 5,
            "color_start": "#7A9C6A",
            "color_end": "#5A7C4A",
            "icon": "eco",
            "order_index": 2,
            "is_active": True,
        },
        {
            "name": "3",
            "min_bonuses": 200000,
            "cashback_percent": 7,
            "color_start": "#5A7C4A",
            "color_end": "#4A6C3A",
            "icon": "eco",
            "order_index": 3,
            "is_active": True,
        },
        {
            "name": "4",
            "min_bonuses": 300000,
            "cashback_percent": 10,
            "color_start": "#4A6C3A",
            "color_end": "#3A5C2A",
            "icon": "eco",
            "order_index": 4,
            "is_active": True,
        },
    ]

    # Удаляем старые текстовые уровни, если они остались от предыдущих версий
    legacy_names = ["Бронза", "Серебро", "Золото", "Алмаз", "Обсидиановый"]
    legacy_levels = (
        db.query(LoyaltyLevelModel)
        .filter(LoyaltyLevelModel.name.in_(legacy_names))
        .all()
    )
    for lvl in legacy_levels:
        print(f"  ✓ Удалён старый уровень: {lvl.name}")
        db.delete(lvl)

    for level_data in levels_data:
        existing = (
            db.query(LoyaltyLevelModel)
            .filter(LoyaltyLevelModel.name == level_data["name"])
            .first()
        )
        if not existing:
            level = LoyaltyLevelModel(**level_data)
            db.add(level)
            print(f"  ✓ Создан уровень: {level_data['name']}")
        else:
            for field, value in level_data.items():
                setattr(existing, field, value)
            print(
                f"  ✓ Обновлён уровень: {level_data['name']} "
                f"(min_bonuses={level_data['min_bonuses']}, "
                f"cashback={level_data['cashback_percent']}%)"
            )

    db.commit()


def create_loyalty_bonuses(db: Session):
    """Создать стандартные бонусы"""
    print("\nСоздание бонусов лояльности...")
    
    bonuses_data = [
        {
            "title": "Приветственный бонус",
            "description": "Получите 50 баллов за первую запись",
            "icon": "card_giftcard",
            "min_level_id": None,
            "order_index": 0,
        },
        {
            "title": "Скидка 5% на все услуги",
            "description": "Постоянная скидка для серебряных членов",
            "icon": "local_offer",
            "min_level_id": None,  # Привязка к уровню можно сделать вручную в админке
            "order_index": 1,
        },
        {
            "title": "Приоритетная запись",
            "description": "Бронируйте время раньше других",
            "icon": "star_outline",
            "min_level_id": None,
            "order_index": 2,
        },
        {
            "title": "Бесплатный апгрейд услуги",
            "description": "Раз в месяц выбирайте любую премиум-опцию бесплатно",
            "icon": "card_giftcard",
            "min_level_id": None,
            "order_index": 3,
        },
    ]
    
    for bonus_data in bonuses_data:
        existing = db.query(LoyaltyBonusModel).filter(
            LoyaltyBonusModel.title == bonus_data["title"]
        ).first()
        if not existing:
            bonus = LoyaltyBonusModel(**bonus_data)
            db.add(bonus)
            print(f"  ✓ Создан бонус: {bonus_data['title']}")
        else:
            print(f"  - Бонус уже существует: {bonus_data['title']}")
    
    db.commit()


def create_categories_and_services(db: Session):
    """Создать категории и услуги"""
    print("\nСоздание категорий и услуг...")
    
    # Категории
    categories_data = [
        {
            "name": "SPA-программы",
            "description": "Комплексные программы для полного расслабления и восстановления",
            "order_index": 0,
        },
        {
            "name": "Массаж",
            "description": "Разнообразие массажных техник для вашего здоровья",
            "order_index": 1,
        },
        {
            "name": "Уход за лицом",
            "description": "Профессиональные процедуры для красоты и молодости кожи",
            "order_index": 2,
        },
    ]
    
    created_categories = {}
    for cat_data in categories_data:
        existing = db.query(ServiceCategory).filter(ServiceCategory.name == cat_data["name"]).first()
        if not existing:
            category = ServiceCategory(**cat_data)
            db.add(category)
            db.flush()
            created_categories[cat_data["name"]] = category
            print(f"  ✓ Создана категория: {cat_data['name']}")
        else:
            created_categories[cat_data["name"]] = existing
            print(f"  - Категория уже существует: {cat_data['name']}")
    
    db.commit()
    
    # Услуги
    services_data = [
        {
            "name": "ORIGINAL HEAD SPA",
            "subtitle": "оригинальный протокол спа головы",
            "description": "Уникальная авторская программа для глубокого расслабления и восстановления кожи головы",
            "price": 5500,
            "duration": 90,
            "category_id": created_categories["SPA-программы"].id,
            "highlights": ["премиум", "расслабление", "уход"],
            "order_index": 0,
        },
        {
            "name": "Релакс-массаж всего тела",
            "subtitle": "классическая техника для снятия напряжения",
            "description": "Общий расслабляющий массаж всего тела с использованием ароматических масел",
            "price": 4000,
            "duration": 60,
            "category_id": created_categories["Массаж"].id,
            "highlights": ["расслабление", "антистресс"],
            "order_index": 0,
        },
        {
            "name": "Массаж горячими камнями",
            "subtitle": "тепло натуральных минералов",
            "description": "Древняя техника с использованием нагретых вулканических камней для глубокого прогрева мышц",
            "price": 6500,
            "duration": 90,
            "category_id": created_categories["Массаж"].id,
            "highlights": ["премиум", "тепло", "релакс"],
            "order_index": 1,
        },
        {
            "name": "Уход за лицом Anti-age",
            "subtitle": "омоложение и лифтинг",
            "description": "Комплексная программа для борьбы с возрастными изменениями кожи",
            "price": 7000,
            "duration": 75,
            "category_id": created_categories["Уход за лицом"].id,
            "highlights": ["премиум", "anti-age", "лифтинг"],
            "order_index": 0,
        },
        {
            "name": "Классический уход за лицом",
            "subtitle": "очищение и увлажнение",
            "description": "Базовая программа для поддержания здоровья и свежести кожи лица",
            "price": 3500,
            "duration": 60,
            "category_id": created_categories["Уход за лицом"].id,
            "highlights": ["очищение", "увлажнение"],
            "order_index": 1,
        },
    ]
    
    for svc_data in services_data:
        existing = db.query(Service).filter(Service.name == svc_data["name"]).first()
        if not existing:
            service = Service(**svc_data)
            db.add(service)
            print(f"  ✓ Создана услуга: {svc_data['name']}")
        else:
            print(f"  - Услуга уже существует: {svc_data['name']}")
    
    db.commit()


def main():
    """Главная функция для запуска скрипта"""
    print("=" * 60)
    print("ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ СТАРТОВЫМИ ДАННЫМИ")
    print("=" * 60)
    
    # Создаём все таблицы, если их ещё нет
    BaseModel.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        create_loyalty_levels(db)
        create_loyalty_bonuses(db)
        create_categories_and_services(db)
        
        print("\n" + "=" * 60)
        print("✓ ГОТОВО! База данных заполнена стартовыми данными.")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ ОШИБКА: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

