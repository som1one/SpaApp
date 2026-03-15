"""
Админские API для управления мастерами и их расписанием
"""
import logging
import enum
from typing import List, Optional
from datetime import time
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.apis.dependencies import admin_required
from app.core.database import get_db
from app.models.staff import Staff, StaffSchedule, StaffService, DayOfWeek
from app.models.service import Service
from app.schemas.staff import (
    StaffResponse,
    StaffCreate,
    StaffUpdate,
    StaffScheduleResponse,
    StaffScheduleCreate,
    StaffScheduleUpdate,
    StaffServiceResponse,
    StaffServiceCreate,
    StaffServiceUpdate,
    StaffWithScheduleResponse,
)
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin/staff", tags=["Admin Staff"])
logger = logging.getLogger(__name__)


def _parse_time(time_str: Optional[str]) -> time:
    """Парсинг времени из строки HH:MM"""
    if not time_str:
        raise HTTPException(status_code=400, detail="Время не может быть пустым")
    
    try:
        # Поддерживаем разные форматы: "HH:MM", "HH:MM:SS"
        if isinstance(time_str, str):
            # Убираем пробелы
            time_str = time_str.strip()
            # Убираем секунды, если есть
            parts = time_str.split(":")
            if len(parts) >= 2:
                hour = int(parts[0].strip())
                minute = int(parts[1].strip())
                if hour < 0 or hour > 23:
                    raise ValueError(f"Часы должны быть от 0 до 23, получено: {hour}")
                if minute < 0 or minute > 59:
                    raise ValueError(f"Минуты должны быть от 0 до 59, получено: {minute}")
                return time(hour, minute)
            else:
                raise ValueError(f"Неверный формат времени: {time_str}. Ожидается HH:MM")
        else:
            raise ValueError(f"Ожидается строка, получен: {type(time_str)}")
    except ValueError as e:
        logger.error(f"Ошибка парсинга времени '{time_str}': {e}")
        raise HTTPException(status_code=400, detail=f"Неверный формат времени: {time_str}. Используйте формат HH:MM (например, 09:00)")
    except Exception as e:
        logger.error(f"Неожиданная ошибка парсинга времени '{time_str}': {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Ошибка парсинга времени: {str(e)}")


def _format_time(t: Optional[time]) -> Optional[str]:
    """Форматирование времени в строку HH:MM"""
    if t is None:
        return None
    return t.strftime("%H:%M")


def _schedule_to_dict(schedule: StaffSchedule) -> dict:
    """Конвертация расписания из БД в словарь для валидации Pydantic"""
    result = {
        "id": schedule.id,
        "staff_id": schedule.staff_id,
        "day_of_week": schedule.day_of_week,
        "start_time": _format_time(schedule.start_time),
        "end_time": _format_time(schedule.end_time),
        "is_active": schedule.is_active,
    }
    # Добавляем опциональные поля только если они есть в схеме
    if schedule.break_start:
        result["break_start"] = _format_time(schedule.break_start)
    if schedule.break_end:
        result["break_end"] = _format_time(schedule.break_end)
    return result


def _serialize_payload_for_audit(payload: dict) -> dict:
    """Сериализация payload для audit service (конвертация time и enum в строки)"""
    serialized = {}
    for key, value in payload.items():
        if isinstance(value, time):
            serialized[key] = _format_time(value)
        elif isinstance(value, (DayOfWeek, enum.Enum)):
            serialized[key] = value.value if hasattr(value, 'value') else str(value)
        elif isinstance(value, dict):
            serialized[key] = _serialize_payload_for_audit(value)
        elif isinstance(value, list):
            serialized[key] = [
                _serialize_payload_for_audit(item) if isinstance(item, dict) else
                (item.value if isinstance(item, enum.Enum) else item)
                for item in value
            ]
        else:
            serialized[key] = value
    return serialized


# Мастера
@router.get("", response_model=List[StaffResponse])
async def list_staff(
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    """Список всех мастеров"""
    staff = db.query(Staff).order_by(Staff.order_index.asc(), Staff.name.asc()).all()
    return [StaffResponse.model_validate(s) for s in staff]


@router.get("/{staff_id}", response_model=StaffWithScheduleResponse)
async def get_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    """Получить информацию о мастере с расписанием и услугами"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Мастер не найден")
    
    schedules = db.query(StaffSchedule).filter(StaffSchedule.staff_id == staff_id).all()
    services = db.query(StaffService).filter(StaffService.staff_id == staff_id).all()
    
    # Создаем словарь для базового StaffResponse (без связанных объектов)
    staff_dict = {
        "id": staff.id,
        "name": staff.name,
        "surname": staff.surname,
        "phone": staff.phone,
        "email": staff.email,
        "specialization": staff.specialization,
        "photo_url": staff.photo_url,
        "description": staff.description,
        "yclients_staff_id": staff.yclients_staff_id,
        "is_active": staff.is_active,
        "order_index": staff.order_index,
    }
    
    # Создаем ответ с правильно отформатированными расписаниями
    result = StaffWithScheduleResponse(
        **staff_dict,
        schedules=[StaffScheduleResponse(**_schedule_to_dict(s)) for s in schedules],
        services=[s.service_id for s in services],
    )
    
    return result


@router.post("", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
async def create_staff(
    payload: StaffCreate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Создать мастера"""
    staff = Staff(**payload.model_dump())
    db.add(staff)
    db.commit()
    db.refresh(staff)
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="create_staff",
        entity="staff",
        entity_id=staff.id,
        payload=payload.model_dump(),
        request=http_request,
    )
    
    return StaffResponse.model_validate(staff)


@router.patch("/{staff_id}", response_model=StaffResponse)
async def update_staff(
    staff_id: int,
    payload: StaffUpdate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Обновить мастера"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Мастер не найден")
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(staff, field, value)
    
    db.commit()
    db.refresh(staff)
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="update_staff",
        entity="staff",
        entity_id=staff_id,
        payload=update_data,
        request=http_request,
    )
    
    return StaffResponse.model_validate(staff)


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(
    staff_id: int,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Удалить мастера"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Мастер не найден")
    
    db.delete(staff)
    db.commit()
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="delete_staff",
        entity="staff",
        entity_id=staff_id,
        request=http_request,
    )


# Расписание
@router.get("/{staff_id}/schedules", response_model=List[StaffScheduleResponse])
async def list_staff_schedules(
    staff_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    """Список расписания мастера"""
    schedules = (
        db.query(StaffSchedule)
        .filter(StaffSchedule.staff_id == staff_id)
        .order_by(StaffSchedule.day_of_week.asc())
        .all()
    )
    # Конвертируем расписания с правильным форматом времени
    return [StaffScheduleResponse(**_schedule_to_dict(s)) for s in schedules]


@router.post("/schedules", response_model=StaffScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_staff_schedule(
    payload: StaffScheduleCreate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Создать расписание для мастера"""
    try:
        logger.info(f"Создание расписания получено: staff_id={payload.staff_id}, day_of_week={payload.day_of_week}, start_time={payload.start_time}, end_time={payload.end_time}")
        
        # Валидируем обязательные поля
        if not payload.start_time:
            raise HTTPException(status_code=400, detail="Поле start_time обязательно")
        if not payload.end_time:
            raise HTTPException(status_code=400, detail="Поле end_time обязательно")
        
        # Проверяем, что мастер существует
        staff = db.query(Staff).filter(Staff.id == payload.staff_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Мастер не найден")
        
        # Проверяем, что день недели валидный
        if payload.day_of_week < 0 or payload.day_of_week > 6:
            raise HTTPException(status_code=400, detail="День недели должен быть от 0 (понедельник) до 6 (воскресенье)")
        
        # Проверяем, нет ли уже расписания на этот день
        existing = (
            db.query(StaffSchedule)
            .filter(
                StaffSchedule.staff_id == payload.staff_id,
                StaffSchedule.day_of_week == DayOfWeek(payload.day_of_week),
            )
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail=f"Расписание на {payload.day_of_week} день недели уже существует")
        
        # Парсим время
        try:
            schedule_data = payload.model_dump(exclude_unset=True)
            schedule_data["start_time"] = _parse_time(schedule_data.get("start_time"))
            schedule_data["end_time"] = _parse_time(schedule_data.get("end_time"))
            if schedule_data.get("break_start"):
                schedule_data["break_start"] = _parse_time(schedule_data["break_start"])
            else:
                schedule_data.pop("break_start", None)
            if schedule_data.get("break_end"):
                schedule_data["break_end"] = _parse_time(schedule_data["break_end"])
            else:
                schedule_data.pop("break_end", None)
            # day_of_week храним как Integer, не конвертируем в enum
            # schedule_data["day_of_week"] остается как int
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка парсинга времени: {e}", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка парсинга времени: {str(e)}. Используйте формат HH:MM (например, 09:00)"
            )
        
        schedule = StaffSchedule(**schedule_data)
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        
        # Сериализуем payload для audit (конвертируем time и enum в строки)
        audit_payload = _serialize_payload_for_audit(payload.model_dump())
        AuditService.log_action(
            db,
            admin_id=admin.id,
            action="create_staff_schedule",
            entity="staff_schedule",
            entity_id=schedule.id,
            payload=audit_payload,
            request=http_request,
        )
        
        # Используем _schedule_to_dict для правильной конвертации времени
        return StaffScheduleResponse(**_schedule_to_dict(schedule))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания расписания: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания расписания: {str(e)}"
        )


@router.patch("/schedules/{schedule_id}", response_model=StaffScheduleResponse)
async def update_staff_schedule(
    schedule_id: int,
    payload: StaffScheduleUpdate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Обновить расписание"""
    schedule = db.query(StaffSchedule).filter(StaffSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    
    update_data = payload.model_dump(exclude_unset=True)
    
    # Парсим время, если оно указано
    if "start_time" in update_data:
        update_data["start_time"] = _parse_time(update_data["start_time"])
    if "end_time" in update_data:
        update_data["end_time"] = _parse_time(update_data["end_time"])
    if "break_start" in update_data and update_data["break_start"]:
        update_data["break_start"] = _parse_time(update_data["break_start"])
    if "break_end" in update_data and update_data["break_end"]:
        update_data["break_end"] = _parse_time(update_data["break_end"])
    if "day_of_week" in update_data:
        update_data["day_of_week"] = DayOfWeek(update_data["day_of_week"])
    
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    db.commit()
    db.refresh(schedule)
    
    # Сериализуем payload для audit (конвертируем time и enum в строки)
    audit_payload = _serialize_payload_for_audit(update_data)
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="update_staff_schedule",
        entity="staff_schedule",
        entity_id=schedule_id,
        payload=audit_payload,
        request=http_request,
    )
    
    # Используем _schedule_to_dict для правильной конвертации времени
    return StaffScheduleResponse(**_schedule_to_dict(schedule))


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff_schedule(
    schedule_id: int,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Удалить расписание"""
    schedule = db.query(StaffSchedule).filter(StaffSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    
    db.delete(schedule)
    db.commit()
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="delete_staff_schedule",
        entity="staff_schedule",
        entity_id=schedule_id,
        request=http_request,
    )


# Привязка мастеров к услугам
@router.post("/services", response_model=StaffServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_staff_service(
    payload: StaffServiceCreate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Привязать мастера к услуге"""
    # Проверяем, что мастер и услуга существуют
    staff = db.query(Staff).filter(Staff.id == payload.staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Мастер не найден")
    
    service = db.query(Service).filter(Service.id == payload.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    
    # Проверяем, нет ли уже такой привязки
    existing = (
        db.query(StaffService)
        .filter(
            StaffService.staff_id == payload.staff_id,
            StaffService.service_id == payload.service_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Мастер уже привязан к этой услуге")
    
    staff_service = StaffService(**payload.model_dump())
    db.add(staff_service)
    db.commit()
    db.refresh(staff_service)
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="create_staff_service",
        entity="staff_service",
        entity_id=staff_service.id,
        payload=payload.model_dump(),
        request=http_request,
    )
    
    return StaffServiceResponse.model_validate(staff_service)


@router.delete("/services/{staff_service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff_service(
    staff_service_id: int,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Удалить привязку мастера к услуге"""
    staff_service = db.query(StaffService).filter(StaffService.id == staff_service_id).first()
    if not staff_service:
        raise HTTPException(status_code=404, detail="Привязка не найдена")
    
    db.delete(staff_service)
    db.commit()
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="delete_staff_service",
        entity="staff_service",
        entity_id=staff_service_id,
        request=http_request,
    )

