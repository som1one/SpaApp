"""Синхронизация услуг и мастеров из YClients в локальную БД.

Запуск:
    python scripts/sync_yclients_catalog.py

Требования:
    - В .env заданы YCLIENTS_ENABLED=True, YCLIENTS_COMPANY_ID, YCLIENTS_API_TOKEN, YCLIENTS_USER_TOKEN
    - Бэкенд может подключиться к базе через settings.DATABASE_URL
"""

from __future__ import annotations

import asyncio
import logging
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
import sys

# Обеспечиваем доступность backend/ в sys.path при запуске напрямую
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.service import Service
from app.models.staff import Staff
from app.services.yclients_service import yclients_service

logger = logging.getLogger("sync_yclients_catalog")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def _to_decimal(value: Any) -> Optional[Decimal]:
    """Аккуратно конвертирует значение в Decimal."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        logger.warning("Не удалось конвертировать цену '%s' в Decimal", value)
        return None


def _safe_int(value: Any) -> Optional[int]:
    """Возвращает целое значение (например, длительность) или None."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


async def _sync_services(db: Session) -> None:
    """Загружает услуги из YClients и создает/обновляет записи в таблице services."""
    services = await yclients_service.get_services()
    if not services:
        logger.warning("YClients не вернул услуги — пропускаем синхронизацию услуг")
        return

    created = 0
    updated = 0

    for order_index, item in enumerate(services):
        yc_id = item.get("id")
        if not yc_id:
            continue

        # Определяем основные поля
        name = (
            item.get("title")
            or item.get("name")
            or f"Услуга из YClients #{yc_id}"
        ).strip()
        description = item.get("description") or item.get("comment") or ""

        price = (
            _to_decimal(item.get("price_min"))
            or _to_decimal(item.get("price"))
            or _to_decimal(item.get("cost"))
        )
        duration = (
            _safe_int(item.get("length"))
            or _safe_int(item.get("duration"))
            or _safe_int(item.get("service_time"))
        )

        category_name = (
            item.get("category_name")
            or (item.get("category") or {}).get("name")
            or None
        )

        image_url = item.get("image") or item.get("photo") or None

        service = (
            db.query(Service)
            .filter(Service.yclients_service_id == yc_id)
            .first()
        )

        if not service:
            # Второй шанс — попытка найти по имени (для уже созданных вручную услуг)
            # Нормализуем имена для сравнения (убираем пробелы, приводим к нижнему регистру)
            normalized_name = name.strip().lower()
            existing_services = db.query(Service).filter(Service.yclients_service_id.is_(None)).all()
            for existing in existing_services:
                if existing.name.strip().lower() == normalized_name:
                    service = existing
                    break

        if not service:
            service = Service(
                name=name,
                description=description,
                price=price,
                duration=duration,
                category=category_name,
                image_url=image_url,
                is_active=True,
                order_index=order_index,
                yclients_service_id=yc_id,
            )
            db.add(service)
            created += 1
        else:
            service.name = name
            service.description = description
            service.price = price if price is not None else service.price
            service.duration = duration or service.duration
            service.category = category_name or service.category
            service.image_url = image_url or service.image_url
            service.order_index = order_index
            service.is_active = True
            service.yclients_service_id = yc_id
            updated += 1

    db.commit()
    logger.info("Услуги синхронизированы: создано %s, обновлено %s", created, updated)


async def _sync_staff(db: Session) -> None:
    """Загружает мастеров из YClients с расписанием и создает/обновляет записи в таблице staff.
    Синхронизируются только те мастера, у которых есть расписание."""
    from datetime import time as dt_time
    from app.models.staff import StaffSchedule
    
    # Получаем мастеров с расписанием
    staff_with_schedule = await yclients_service.get_staff_with_schedule()
    
    if not staff_with_schedule:
        logger.warning("YClients не вернул мастеров с расписанием — пропускаем синхронизацию мастеров")
        return

    created = 0
    updated = 0
    schedules_created = 0

    for order_index, (yc_id, staff_data) in enumerate(staff_with_schedule.items()):
        staff_info = staff_data.get("staff_info", {})
        schedule_list = staff_data.get("schedule", [])
        
        # Пропускаем только если расписание явно None или пустой список после попыток получить его
        # Если мастер найден, но расписание не извлечено, всё равно добавляем мастера (без расписания)

        full_name = (staff_info.get("name") or "").strip()
        if not full_name:
            full_name = f"Мастер #{yc_id}"
        
        # Разбиваем имя на имя/фамилию (если возможно)
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0] if name_parts else f"Мастер #{yc_id}"
        surname = name_parts[1] if len(name_parts) > 1 else None

        specialization = (
            staff_info.get("specialization")
            or staff_info.get("profession")
            or None
        )
        photo_url = staff_info.get("avatar") or staff_info.get("image_url") or None
        description = staff_info.get("comment") or staff_info.get("about") or None
        phone = staff_info.get("phone") or None
        email = staff_info.get("email") or None

        # Ищем существующего мастера
        staff = (
            db.query(Staff)
            .filter(Staff.yclients_staff_id == yc_id)
            .first()
        )

        if not staff:
            # Пытаемся найти по имени
            normalized_name = first_name.strip().lower()
            existing_staff = db.query(Staff).filter(Staff.yclients_staff_id.is_(None)).all()
            for existing in existing_staff:
                if existing.name.strip().lower() == normalized_name:
                    staff = existing
                    break

        if not staff:
            staff = Staff(
                name=first_name,
                surname=surname,
                phone=phone,
                email=email,
                specialization=specialization,
                photo_url=photo_url,
                description=description,
                is_active=True,
                order_index=order_index,
                yclients_staff_id=yc_id,
            )
            db.add(staff)
            db.flush()  # Получаем ID для связывания расписания
            created += 1
        else:
            staff.name = first_name or staff.name
            staff.surname = surname or staff.surname
            staff.phone = phone or staff.phone
            staff.email = email or staff.email
            staff.specialization = specialization or staff.specialization
            staff.photo_url = photo_url or staff.photo_url
            staff.description = description or staff.description
            staff.is_active = True
            staff.order_index = order_index
            staff.yclients_staff_id = yc_id
            updated += 1

        # Синхронизируем расписание
        # Сначала удаляем старое расписание для этого мастера
        db.query(StaffSchedule).filter(StaffSchedule.staff_id == staff.id).delete()
        
        # Добавляем новое расписание
        for schedule_item in schedule_list:
            day_of_week = schedule_item.get("day_of_week")
            start_time_str = schedule_item.get("start_time", "09:00")
            end_time_str = schedule_item.get("end_time", "18:00")
            break_start_str = schedule_item.get("break_start")
            break_end_str = schedule_item.get("break_end")
            
            # Парсим время
            try:
                start_parts = start_time_str.split(":")
                start_time = dt_time(int(start_parts[0]), int(start_parts[1]) if len(start_parts) > 1 else 0)
                
                end_parts = end_time_str.split(":")
                end_time = dt_time(int(end_parts[0]), int(end_parts[1]) if len(end_parts) > 1 else 0)
                
                break_start = None
                break_end = None
                if break_start_str:
                    break_parts = break_start_str.split(":")
                    break_start = dt_time(int(break_parts[0]), int(break_parts[1]) if len(break_parts) > 1 else 0)
                if break_end_str:
                    break_parts = break_end_str.split(":")
                    break_end = dt_time(int(break_parts[0]), int(break_parts[1]) if len(break_parts) > 1 else 0)
                
                schedule = StaffSchedule(
                    staff_id=staff.id,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    break_start=break_start,
                    break_end=break_end,
                    is_active=True,
                )
                db.add(schedule)
                schedules_created += 1
            except Exception as e:
                logger.error(f"Ошибка создания расписания для мастера {staff.id}, день {day_of_week}: {e}")
                continue

    db.commit()
    logger.info(
        "Мастера с расписанием синхронизированы: создано %s, обновлено %s, расписаний создано %s",
        created, updated, schedules_created
    )


async def main() -> None:
    if not settings.YCLIENTS_ENABLED:
        logger.error("YClients интеграция отключена (YCLIENTS_ENABLED=False) — синхронизация невозможна")
        return

    if not settings.YCLIENTS_COMPANY_ID or not settings.YCLIENTS_API_TOKEN or not settings.YCLIENTS_USER_TOKEN:
        logger.error(
            "Не заданы YCLIENTS_COMPANY_ID / YCLIENTS_API_TOKEN / YCLIENTS_USER_TOKEN. "
            "Проверьте файл .env"
        )
        return

    logger.info("Начинаем синхронизацию каталога из YClients для компании %s", settings.YCLIENTS_COMPANY_ID)
    yclients_service.configure(
        company_id=settings.YCLIENTS_COMPANY_ID,
        api_token=settings.YCLIENTS_API_TOKEN,
        user_token=settings.YCLIENTS_USER_TOKEN,
    )

    db: Session = SessionLocal()
    try:
        await _sync_services(db)
        await _sync_staff(db)
    finally:
        db.close()
        logger.info("Синхронизация завершена")


if __name__ == "__main__":
    asyncio.run(main())

