"""
API endpoints для интеграции с YClients
"""
import logging
from typing import Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.service import Service
from app.services.yclients_service import yclients_service
from app.services.loyalty_service import award_loyalty_for_booking

router = APIRouter(prefix="/yclients", tags=["YClients"])
logger = logging.getLogger(__name__)


# Настройка YClients будет происходить при первом запросе


@router.get("/available-dates/{service_id}")
async def get_available_dates(
    service_id: int,
    staff_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить доступные даты и время для записи из YClients
    
    Args:
        service_id: ID услуги в нашей БД
        staff_id: ID мастера в YClients (опционально)
        date_from: Начальная дата (по умолчанию сегодня)
        date_to: Конечная дата (по умолчанию +30 дней)
    """
    if not settings.YCLIENTS_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YClients интеграция не включена"
        )
    
    # Настраиваем YClients при первом запросе
    if settings.YCLIENTS_COMPANY_ID:
        yclients_service.configure(
            company_id=settings.YCLIENTS_COMPANY_ID,
            api_token=settings.YCLIENTS_API_TOKEN,
            user_token=settings.YCLIENTS_USER_TOKEN,
        )
    
    # Получаем услугу из БД
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена"
        )
    
    if not service.yclients_service_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Услуга не привязана к YClients"
        )
    
    # Определяем даты
    if not date_from:
        date_from = date.today()
    if not date_to:
        date_to = date.today() + timedelta(days=30)
    
    # Получаем доступные слоты из YClients
    available_dates = await yclients_service.get_available_dates(
        service_id=service.yclients_service_id,
        staff_id=staff_id or service.yclients_staff_id,
        date_from=date_from,
        date_to=date_to,
    )
    
    return {
        "service_id": service_id,
        "service_name": service.name,
        "available_dates": available_dates,
    }


@router.post("/book/{service_id}")
async def create_yclients_booking(
    service_id: int,
    datetime_str: str,
    client_name: str,
    client_phone: str,
    client_email: Optional[str] = None,
    comment: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создать запись в YClients
    
    Args:
        service_id: ID услуги в нашей БД
        datetime_str: Дата и время в формате "YYYY-MM-DD HH:MM"
        client_name: Имя клиента
        client_phone: Телефон клиента
        client_email: Email клиента (опционально)
        comment: Комментарий (опционально)
    """
    if not settings.YCLIENTS_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YClients интеграция не включена"
        )
    
    # Получаем услугу из БД
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена"
        )
    
    if not service.yclients_service_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Услуга не привязана к YClients"
        )
    
    # Используем данные пользователя, если не указаны
    if not client_name:
        client_name = f"{current_user.name or ''} {current_user.surname or ''}".strip() or current_user.email
    if not client_email:
        client_email = current_user.email
    
    # Создаём запись в YClients
    booking = await yclients_service.create_booking(
        service_id=service.yclients_service_id,
        datetime_str=datetime_str,
        client_name=client_name,
        client_phone=client_phone,
        client_email=client_email,
        staff_id=service.yclients_staff_id,
        comment=comment,
    )
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать запись в YClients"
        )
    
    # Также создаём запись в нашей БД для истории
    from app.models.booking import Booking, BookingStatus
    from datetime import datetime as dt
    
    try:
        appointment_dt = dt.strptime(datetime_str, "%Y-%m-%d %H:%M")
        our_booking = Booking(
            user_id=current_user.id,
            service_name=service.name,
            service_duration=service.duration,
            service_price=int(service.price * 100) if service.price else None,
            appointment_datetime=appointment_dt,
            status=BookingStatus.CONFIRMED,  # YClients подтверждает автоматически
            notes=comment or f"Запись через YClients. ID: {booking.get('id')}",
            phone=client_phone,
        )
        db.add(our_booking)
        db.commit()
        db.refresh(our_booking)
        
        logger.info(f"Запись создана в YClients и нашей БД: {our_booking.id}")
        
    except Exception as e:
        logger.error(f"Ошибка создания записи в нашей БД: {e}", exc_info=True)
        # Не падаем, если не удалось создать в нашей БД
    
    return {
        "success": True,
        "yclients_booking_id": booking.get("id"),
        "booking": booking,
    }


@router.get("/widget-url/{service_id}")
async def get_widget_url(
    service_id: int,
):
    """
    Получить URL формы записи YClients
    
    Просто возвращает ссылку на форму записи
    """
    if not settings.YCLIENTS_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YClients интеграция не включена"
        )
    
    # Просто возвращаем URL формы
    widget_url = settings.YCLIENTS_BOOKING_FORM_URL or f"https://n239661.yclients.com"
    
    return {
        "widget_url": widget_url.rstrip('/'),
    }


@router.post("/sync-bookings")
async def sync_bookings(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Синхронизировать записи из YClients с локальной БД
    
    Получает записи из YClients и создает/обновляет их в нашей БД
    """
    if not settings.YCLIENTS_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YClients интеграция не включена"
        )
    
    # Настраиваем YClients
    if settings.YCLIENTS_COMPANY_ID:
        yclients_service.configure(
            company_id=settings.YCLIENTS_COMPANY_ID,
            api_token=settings.YCLIENTS_API_TOKEN,
            user_token=settings.YCLIENTS_USER_TOKEN,
        )
    
    # Определяем даты
    if not date_from:
        date_from = date.today()
    if not date_to:
        date_to = date.today() + timedelta(days=30)
    
    try:
        # Получаем записи из YClients
        yclients_bookings = await yclients_service.get_bookings(
            date_from=date_from,
            date_to=date_to,
        )
        
        if not yclients_bookings:
            return {
                "success": True,
                "synced_count": 0,
                "message": "Нет записей для синхронизации"
            }
        
        # Импортируем модели
        from app.models.booking import Booking, BookingStatus
        
        synced_count = 0
        updated_count = 0
        created_count = 0
        
        for yc_booking in yclients_bookings:
            try:
                # Пытаемся найти запись по ID из YClients (храним в notes)
                yc_booking_id = str(yc_booking.get("id", ""))
                
                # Ищем существующую запись
                existing_booking = db.query(Booking).filter(
                    Booking.notes.contains(f"YClients. ID: {yc_booking_id}")
                ).first()
                
                # Парсим дату и время
                appointment_dt_str = yc_booking.get("date", "")
                appointment_time_str = yc_booking.get("time", "")
                
                if not appointment_dt_str or not appointment_time_str:
                    continue
                
                appointment_dt = datetime.strptime(
                    f"{appointment_dt_str} {appointment_time_str}",
                    "%Y-%m-%d %H:%M"
                )
                
                # Получаем данные клиента
                client = yc_booking.get("client", {})
                client_name = client.get("name", "")
                client_phone = client.get("phone", "")
                client_email = client.get("email", "")
                
                # Получаем данные услуги
                services = yc_booking.get("services", [])
                service_name = ""
                service_price = None
                service_duration = None
                
                if services and len(services) > 0:
                    service = services[0]
                    service_name = service.get("title", "") or service.get("name", "")
                    service_price = service.get("price_min", None)
                    service_duration = service.get("length", None)
                
                # Определяем статус
                yc_status = yc_booking.get("status", "").lower()
                if yc_status in ["confirmed", "confirmed_online"]:
                    booking_status = BookingStatus.CONFIRMED
                elif yc_status in ["completed", "done"]:
                    booking_status = BookingStatus.COMPLETED
                elif yc_status in ["cancelled", "deleted"]:
                    booking_status = BookingStatus.CANCELLED
                else:
                    booking_status = BookingStatus.PENDING
                
                # Ищем пользователя по email или телефону
                from app.models.user import User
                user = None
                if client_email:
                    user = db.query(User).filter(User.email == client_email).first()
                if not user and client_phone:
                    # Нормализуем телефон
                    phone_digits = ''.join(filter(str.isdigit, client_phone))
                    if phone_digits:
                        user = db.query(User).filter(User.phone.contains(phone_digits[-10:])).first()
                
                # Если пользователь не найден, пропускаем запись
                if not user:
                    logger.warning(f"Пользователь не найден для записи YClients {yc_booking_id}")
                    continue
                
                if existing_booking:
                    # Обновляем существующую запись
                    existing_booking.service_name = service_name or existing_booking.service_name
                    existing_booking.service_duration = service_duration or existing_booking.service_duration
                    existing_booking.service_price = int(service_price * 100) if service_price else existing_booking.service_price
                    existing_booking.appointment_datetime = appointment_dt
                    existing_booking.status = booking_status
                    existing_booking.phone = client_phone or existing_booking.phone
                    existing_booking.notes = f"Запись через YClients. ID: {yc_booking_id}"
                    updated_count += 1
                else:
                    # Создаем новую запись
                    new_booking = Booking(
                        user_id=user.id,
                        service_name=service_name or "Услуга из YClients",
                        service_duration=service_duration,
                        service_price=int(service_price * 100) if service_price else None,
                        appointment_datetime=appointment_dt,
                        status=booking_status,
                        phone=client_phone,
                        notes=f"Запись через YClients. ID: {yc_booking_id}",
                    )
                    db.add(new_booking)
                    created_count += 1
                
                synced_count += 1
                
            except Exception as e:
                logger.error(f"Ошибка синхронизации записи {yc_booking.get('id')}: {e}", exc_info=True)
                continue
        
        db.commit()
        
        return {
            "success": True,
            "synced_count": synced_count,
            "created_count": created_count,
            "updated_count": updated_count,
            "message": f"Синхронизировано {synced_count} записей"
        }
        
    except Exception as e:
        logger.error(f"Ошибка синхронизации записей из YClients: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка синхронизации: {str(e)}"
        )


@router.post("/webhook")
async def yclients_webhook(
    payload: dict,
    db: Session = Depends(get_db),
):
    """
    Webhook от YClients для уведомлений о изменениях записей
    
    YClients может отправлять уведомления о:
    - Создании новой записи
    - Изменении статуса записи
    - Отмене записи
    
    Настройка webhook в YClients:
    Настройки → Интеграции → Webhooks → Добавить URL
    """
    if not settings.YCLIENTS_ENABLED:
        logger.warning("YClients webhook получен, но интеграция не включена")
        return {"status": "ignored"}
    
    logger.info(f"Получен webhook от YClients: {payload}")
    
    try:
        # Определяем тип события
        event_type = payload.get("event", "")
        record_data = payload.get("data", {})
        
        if not record_data:
            return {"status": "ok", "message": "Нет данных записи"}
        
        # Настраиваем YClients для получения полных данных
        if settings.YCLIENTS_COMPANY_ID:
            yclients_service.configure(
                company_id=settings.YCLIENTS_COMPANY_ID,
                api_token=settings.YCLIENTS_API_TOKEN,
                user_token=settings.YCLIENTS_USER_TOKEN,
            )
        
        record_id = record_data.get("id")
        if not record_id:
            return {"status": "ok", "message": "Нет ID записи"}
        
        # Получаем полные данные записи из YClients
        full_booking = await yclients_service.get_booking_by_id(record_id)
        if not full_booking:
            logger.warning(f"Не удалось получить данные записи {record_id} из YClients")
            return {"status": "ok", "message": "Запись не найдена в YClients"}
        
        # Синхронизируем эту конкретную запись
        from app.models.booking import Booking, BookingStatus
        from app.models.user import User
        
        yc_booking = full_booking
        
        # Парсим дату и время
        appointment_dt_str = yc_booking.get("date", "")
        appointment_time_str = yc_booking.get("time", "")
        
        if not appointment_dt_str or not appointment_time_str:
            return {"status": "ok", "message": "Некорректная дата записи"}
        
        try:
            appointment_dt = datetime.strptime(
                f"{appointment_dt_str} {appointment_time_str}",
                "%Y-%m-%d %H:%M"
            )
        except ValueError:
            return {"status": "ok", "message": "Некорректный формат даты записи"}
        
        # Получаем данные клиента
        client = yc_booking.get("client", {})
        client_email = client.get("email", "")
        client_phone = client.get("phone", "")
        
        # Ищем пользователя
        user = None
        
        # Сначала пытаемся найти по уникальному коду из комментария
        comment = yc_booking.get("comment", "") or ""
        if "Код клиента:" in comment:
            try:
                code_start = comment.find("Код клиента:") + len("Код клиента:")
                unique_code = comment[code_start:].strip().split()[0]  # Берем первое слово после "Код клиента:"
                user = db.query(User).filter(User.unique_code == unique_code).first()
                if user:
                    logger.info(f"Пользователь найден по уникальному коду {unique_code} для записи {record_id}")
            except Exception as e:
                logger.debug(f"Ошибка извлечения кода из комментария: {e}")
        
        # Если не нашли по коду, ищем по email
        if not user and client_email:
            user = db.query(User).filter(User.email == client_email).first()
            if user:
                logger.info(f"Пользователь найден по email для записи {record_id}")
        
        # Если не нашли по email, ищем по телефону
        if not user and client_phone:
            phone_digits = ''.join(filter(str.isdigit, client_phone))
            if phone_digits:
                user = db.query(User).filter(User.phone.contains(phone_digits[-10:])).first()
                if user:
                    logger.info(f"Пользователь найден по телефону для записи {record_id}")
        
        if not user:
            logger.warning(f"Пользователь не найден для записи {record_id} (email: {client_email}, phone: {client_phone}, comment: {comment[:50]})")
            return {"status": "ok", "message": "Пользователь не найден"}
        
        # Получаем данные услуги
        services = yc_booking.get("services", [])
        service_name = ""
        service_price = None
        service_duration = None
        
        if services and len(services) > 0:
            service = services[0]
            service_name = service.get("title", "") or service.get("name", "")
            service_price = service.get("price_min", None)
            service_duration = service.get("length", None)
        
        # Определяем статус
        yc_status = yc_booking.get("status", "").lower()
        if yc_status in ["confirmed", "confirmed_online"]:
            booking_status = BookingStatus.CONFIRMED
        elif yc_status in ["completed", "done"]:
            booking_status = BookingStatus.COMPLETED
        elif yc_status in ["cancelled", "deleted"]:
            booking_status = BookingStatus.CANCELLED
        else:
            booking_status = BookingStatus.PENDING
        
        # Ищем существующую запись по YClients ID
        existing_booking = db.query(Booking).filter(
            Booking.notes.contains(f"YClients. ID: {record_id}")
        ).first()
        
        # Если не нашли по ID, ищем по уникальному коду пользователя и дате
        if not existing_booking and user and user.unique_code:
            appointment_dt = datetime.strptime(
                f"{appointment_dt_str} {appointment_time_str}",
                "%Y-%m-%d %H:%M"
            )
            existing_booking = db.query(Booking).filter(
                Booking.user_id == user.id,
                Booking.appointment_datetime == appointment_dt,
                Booking.notes.contains(f"Код клиента: {user.unique_code}")
            ).first()
        
        if existing_booking:
            # Обновляем существующую запись
            existing_booking.service_name = service_name or existing_booking.service_name
            existing_booking.service_duration = service_duration or existing_booking.service_duration
            existing_booking.service_price = int(service_price * 100) if service_price else existing_booking.service_price
            existing_booking.appointment_datetime = appointment_dt
            existing_booking.status = booking_status
            existing_booking.phone = client_phone or existing_booking.phone
            # Обновляем заметки с YClients ID и уникальным кодом
            notes_parts = [f"Запись через YClients. ID: {record_id}"]
            if user.unique_code:
                notes_parts.append(f"Код клиента: {user.unique_code}")
            existing_booking.notes = ". ".join(notes_parts)
            if booking_status == BookingStatus.CANCELLED:
                from app.utils.timezone import moscow_now
                existing_booking.cancelled_at = moscow_now()
            # Начисляем лояльность, если запись завершена
            award_loyalty_for_booking(db, user, existing_booking)
        else:
            # Создаем новую запись
            # Формируем заметки с YClients ID и уникальным кодом
            notes_parts = [f"Запись через YClients. ID: {record_id}"]
            if user.unique_code:
                notes_parts.append(f"Код клиента: {user.unique_code}")
            
            new_booking = Booking(
                user_id=user.id,
                service_name=service_name or "Услуга из YClients",
                service_duration=service_duration,
                service_price=int(service_price * 100) if service_price else None,
                appointment_datetime=appointment_dt,
                status=booking_status,
                phone=client_phone,
                notes=". ".join(notes_parts),
            )
            if booking_status == BookingStatus.CANCELLED:
                from app.utils.timezone import moscow_now
                new_booking.cancelled_at = moscow_now()
            db.add(new_booking)
            # Начисляем лояльность, если запись завершена
            award_loyalty_for_booking(db, user, new_booking)
        
        db.commit()
        
        logger.info(f"Запись {record_id} успешно синхронизирована через webhook")
        
        return {"status": "ok", "message": "Запись синхронизирована"}
        
    except Exception as e:
        logger.error(f"Ошибка обработки webhook от YClients: {e}", exc_info=True)
        db.rollback()
        return {"status": "error", "message": str(e)}

