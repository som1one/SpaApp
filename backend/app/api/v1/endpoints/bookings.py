"""
API endpoints для записей на прием
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import (
    BookingCreate, BookingUpdate, BookingResponse, BookingStatusEnum
)
from app.utils.email import send_booking_confirmation
from app.utils.timezone import moscow_now

router = APIRouter(prefix="/bookings", tags=["Bookings"])
logger = logging.getLogger(__name__)


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: BookingCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание новой записи на прием"""
    logger.info(
        "Создание бронирования",
        extra={
            "user_id": current_user.id,
            "email": current_user.email,
            "service": booking.service_name,
            "appointment": booking.appointment_datetime.isoformat() if booking.appointment_datetime else None,
        },
    )

    if booking.appointment_datetime <= moscow_now():
        logger.warning("Попытка создать бронирование в прошлом", extra={"user_id": current_user.id})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дата записи должна быть в будущем"
        )

    new_booking = Booking(
        user_id=current_user.id,
        service_name=booking.service_name,
        service_duration=booking.service_duration,
        service_price=booking.service_price,
        appointment_datetime=booking.appointment_datetime,
        status=BookingStatus.PENDING,
        notes=booking.notes,
        phone=booking.phone or current_user.email  # Используем email если телефон не указан
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    logger.info(
        "Бронирование создано",
        extra={
            "booking_id": new_booking.id,
            "user_email": current_user.email,
        },
    )

    background_tasks.add_task(
        send_booking_confirmation,
        email=current_user.email,
        service_name=booking.service_name,
        appointment_datetime=booking.appointment_datetime,
        service_price=booking.service_price,
        service_duration=booking.service_duration
    )

    return BookingResponse(
        id=new_booking.id,
        user_id=new_booking.user_id,
        service_name=new_booking.service_name,
        service_duration=new_booking.service_duration,
        service_price=new_booking.service_price,
        appointment_datetime=new_booking.appointment_datetime,
        status=new_booking.status.value,
        notes=new_booking.notes,
        phone=new_booking.phone,
        cancelled_at=new_booking.cancelled_at,
        cancelled_reason=new_booking.cancelled_reason,
        created_at=new_booking.created_at,
        updated_at=new_booking.updated_at,
    )


@router.get("", response_model=List[BookingResponse])
async def get_bookings(
    status_filter: Optional[BookingStatusEnum] = Query(None, alias="status"),
    upcoming_only: bool = Query(False, description="Только предстоящие записи"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить список записей текущего пользователя
    
    Args:
        status_filter: Фильтр по статусу (pending, confirmed, completed, cancelled)
        upcoming_only: Если True, возвращает только предстоящие записи (не завершенные и не отмененные)
    """
    from datetime import datetime
    
    query = db.query(Booking).filter(Booking.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Booking.status == BookingStatus(status_filter.value))
    
    # Фильтр для предстоящих записей
    if upcoming_only:
        query = query.filter(
            Booking.appointment_datetime >= moscow_now(),
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        )
    
    bookings = query.order_by(Booking.appointment_datetime.asc() if upcoming_only else Booking.appointment_datetime.desc()).offset(skip).limit(limit).all()
    
    return [
        BookingResponse(
            id=booking.id,
            user_id=booking.user_id,
            service_name=booking.service_name,
            service_duration=booking.service_duration,
            service_price=booking.service_price,
            appointment_datetime=booking.appointment_datetime,
            status=booking.status.value,
            notes=booking.notes,
            phone=booking.phone,
            cancelled_at=booking.cancelled_at,
            cancelled_reason=booking.cancelled_reason,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
        )
        for booking in bookings
    ]


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить запись по ID"""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена"
        )
    
    return BookingResponse(
        id=booking.id,
        user_id=booking.user_id,
        service_name=booking.service_name,
        service_duration=booking.service_duration,
        service_price=booking.service_price,
        appointment_datetime=booking.appointment_datetime,
        status=booking.status.value,
        notes=booking.notes,
        phone=booking.phone,
        cancelled_at=booking.cancelled_at,
        cancelled_reason=booking.cancelled_reason,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить запись"""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена"
        )
    
    # Проверка, что нельзя изменить отмененную или завершенную запись
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя изменить отмененную запись"
        )
    
    if booking.status == BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя изменить завершенную запись"
        )
    
    # Обновление полей
    if booking_update.service_name is not None:
        booking.service_name = booking_update.service_name
    if booking_update.service_duration is not None:
        booking.service_duration = booking_update.service_duration
    if booking_update.service_price is not None:
        booking.service_price = booking_update.service_price
    if booking_update.appointment_datetime is not None:
        booking.appointment_datetime = booking_update.appointment_datetime
    if booking_update.status is not None:
        booking.status = BookingStatus(booking_update.status.value)
    if booking_update.notes is not None:
        booking.notes = booking_update.notes
    if booking_update.phone is not None:
        booking.phone = booking_update.phone
    
    # Обработка отмены
    if booking_update.status == BookingStatusEnum.CANCELLED:
        booking.cancelled_at = moscow_now()
        if booking_update.cancelled_reason:
            booking.cancelled_reason = booking_update.cancelled_reason
        
        # Если запись из YClients, пытаемся отменить её там тоже
        if booking.notes and "YClients. ID:" in booking.notes:
            try:
                # Извлекаем ID записи из YClients из notes
                import re
                match = re.search(r'YClients\. ID:\s*(\d+)', booking.notes)
                if match:
                    yclients_record_id = int(match.group(1))
                    
                    # Пытаемся отменить запись в YClients
                    if settings.YCLIENTS_ENABLED:
                        from app.services.yclients_service import yclients_service
                        yclients_service.configure(
                            company_id=settings.YCLIENTS_COMPANY_ID,
                            api_token=settings.YCLIENTS_API_TOKEN,
                            user_token=settings.YCLIENTS_USER_TOKEN,
                        )
                        
                        # Отменяем запись в YClients
                        cancelled_reason = booking_update.cancelled_reason or "Отменено пользователем"
                        success = await yclients_service.cancel_booking(
                            record_id=yclients_record_id,
                            reason=cancelled_reason
                        )
                        
                        if success:
                            logger.info(f"Запись {booking.id} успешно отменена в YClients (ID: {yclients_record_id})")
                        else:
                            logger.warning(f"Не удалось отменить запись {yclients_record_id} в YClients. "
                                         f"Рекомендуется отменить её вручную в YClients.")
            except Exception as e:
                logger.warning(f"Не удалось обработать отмену записи YClients: {e}")
                # Не падаем, если не удалось отменить в YClients
    
    db.commit()
    db.refresh(booking)
    
    return BookingResponse(
        id=booking.id,
        user_id=booking.user_id,
        service_name=booking.service_name,
        service_duration=booking.service_duration,
        service_price=booking.service_price,
        appointment_datetime=booking.appointment_datetime,
        status=booking.status.value,
        notes=booking.notes,
        phone=booking.phone,
        cancelled_at=booking.cancelled_at,
        cancelled_reason=booking.cancelled_reason,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить запись"""
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена"
        )
    
    db.delete(booking)
    db.commit()
    
    return None

