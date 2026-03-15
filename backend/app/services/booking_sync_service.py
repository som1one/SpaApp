"""
Сервис для периодической синхронизации бронирований из YClients
"""
import logging
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.yclients_service import yclients_service
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.services.loyalty_service import award_loyalty_for_booking

logger = logging.getLogger(__name__)


async def sync_yclients_bookings():
    """
    Периодическая синхронизация бронирований из YClients
    
    Запускается по расписанию (например, каждые 30 минут)
    """
    if not settings.YCLIENTS_ENABLED:
        logger.debug("YClients интеграция не включена, пропускаем синхронизацию")
        return
    
    logger.info("Начало периодической синхронизации бронирований из YClients")
    
    # Настраиваем YClients
    if not settings.YCLIENTS_COMPANY_ID:
        logger.warning("YClients COMPANY_ID не настроен")
        return
    
    yclients_service.configure(
        company_id=settings.YCLIENTS_COMPANY_ID,
        api_token=settings.YCLIENTS_API_TOKEN,
        user_token=settings.YCLIENTS_USER_TOKEN,
    )
    
    db: Session = SessionLocal()
    try:
        # Синхронизируем записи на ближайшие 30 дней
        date_from = date.today()
        date_to = date.today() + timedelta(days=30)
        
        # Получаем записи из YClients
        yclients_bookings = await yclients_service.get_bookings(
            date_from=date_from,
            date_to=date_to,
        )
        
        if not yclients_bookings:
            logger.info("Нет записей для синхронизации из YClients")
            return
        
        logger.info(f"Получено {len(yclients_bookings)} записей из YClients для синхронизации")
        
        synced_count = 0
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for yc_booking in yclients_bookings:
            try:
                yc_booking_id = str(yc_booking.get("id", ""))
                
                if not yc_booking_id:
                    continue
                
                # Парсим дату и время
                appointment_dt_str = yc_booking.get("date", "")
                appointment_time_str = yc_booking.get("time", "")
                
                if not appointment_dt_str or not appointment_time_str:
                    logger.debug(f"Пропущена запись {yc_booking_id}: нет даты или времени")
                    skipped_count += 1
                    continue
                
                try:
                    appointment_dt = datetime.strptime(
                        f"{appointment_dt_str} {appointment_time_str}",
                        "%Y-%m-%d %H:%M"
                    )
                except ValueError as e:
                    logger.warning(f"Не удалось распарсить дату/время для записи {yc_booking_id}: {appointment_dt_str} {appointment_time_str} - {e}")
                    skipped_count += 1
                    continue
                
                # Получаем данные клиента
                client = yc_booking.get("client", {})
                client_email = client.get("email", "")
                client_phone = client.get("phone", "")
                
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
                            logger.debug(f"Пользователь найден по уникальному коду {unique_code} для записи {yc_booking_id}")
                    except Exception as e:
                        logger.debug(f"Ошибка извлечения кода из комментария: {e}")
                
                # Если не нашли по коду, ищем по email
                if not user and client_email:
                    user = db.query(User).filter(User.email == client_email).first()
                    if user:
                        logger.debug(f"Пользователь найден по email для записи {yc_booking_id}")
                
                # Если не нашли по email, ищем по телефону
                if not user and client_phone:
                    phone_digits = ''.join(filter(str.isdigit, client_phone))
                    if phone_digits:
                        # Пробуем разные варианты поиска по телефону
                        user = db.query(User).filter(User.phone.contains(phone_digits[-10:])).first()
                        if not user and len(phone_digits) >= 10:
                            # Пробуем без последних цифр
                            user = db.query(User).filter(User.phone.contains(phone_digits[-9:])).first()
                        if user:
                            logger.debug(f"Пользователь найден по телефону для записи {yc_booking_id}")
                
                if not user:
                    skipped_count += 1
                    logger.debug(f"Пользователь не найден для записи YClients {yc_booking_id} (email: {client_email}, phone: {client_phone}, comment: {comment[:50]})")
                    continue
                
                # Ищем существующую запись по YClients ID
                existing_booking = db.query(Booking).filter(
                    Booking.notes.contains(f"YClients. ID: {yc_booking_id}")
                ).first()
                
                # Если не нашли по ID, ищем по уникальному коду пользователя и дате
                if not existing_booking and user.unique_code:
                    existing_booking = db.query(Booking).filter(
                        Booking.user_id == user.id,
                        Booking.appointment_datetime == appointment_dt,
                        Booking.notes.contains(f"Код клиента: {user.unique_code}")
                    ).first()
                
                if existing_booking:
                    # Обновляем существующую запись
                    existing_booking.service_name = service_name or existing_booking.service_name
                    existing_booking.service_duration = service_duration or existing_booking.service_duration
                    if service_price:
                        try:
                            existing_booking.service_price = int(service_price * 100)
                        except (ValueError, TypeError):
                            logger.warning(f"Не удалось конвертировать цену {service_price} для записи {yc_booking_id}")
                    existing_booking.appointment_datetime = appointment_dt
                    existing_booking.status = booking_status
                    existing_booking.phone = client_phone or existing_booking.phone
                    # Обновляем заметки с YClients ID и уникальным кодом
                    notes_parts = [f"Запись через YClients. ID: {yc_booking_id}"]
                    if user.unique_code:
                        notes_parts.append(f"Код клиента: {user.unique_code}")
                    existing_booking.notes = ". ".join(notes_parts)
                    if booking_status == BookingStatus.CANCELLED and not existing_booking.cancelled_at:
                        from app.utils.timezone import moscow_now
                        existing_booking.cancelled_at = moscow_now()
                    # Начисляем лояльность, если запись завершена
                    try:
                        award_loyalty_for_booking(db, user, existing_booking)
                    except Exception as e:
                        logger.warning(f"Не удалось начислить лояльность для записи {yc_booking_id}: {e}")
                    updated_count += 1
                else:
                    # Создаем новую запись
                    try:
                        service_price_cents = int(service_price * 100) if service_price else None
                    except (ValueError, TypeError):
                        service_price_cents = None
                        logger.warning(f"Не удалось конвертировать цену {service_price} для записи {yc_booking_id}")
                    
                    # Формируем заметки с YClients ID и уникальным кодом
                    notes_parts = [f"Запись через YClients. ID: {yc_booking_id}"]
                    if user.unique_code:
                        notes_parts.append(f"Код клиента: {user.unique_code}")
                    
                    new_booking = Booking(
                        user_id=user.id,
                        service_name=service_name or "Услуга из YClients",
                        service_duration=service_duration,
                        service_price=service_price_cents,
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
                    try:
                        award_loyalty_for_booking(db, user, new_booking)
                    except Exception as e:
                        logger.warning(f"Не удалось начислить лояльность для новой записи {yc_booking_id}: {e}")
                    created_count += 1
                
                synced_count += 1
                
            except Exception as e:
                logger.error(f"Ошибка синхронизации записи {yc_booking.get('id')}: {e}", exc_info=True)
                skipped_count += 1
                continue
        
        db.commit()
        
        logger.info(
            f"Синхронизация завершена: создано {created_count}, обновлено {updated_count}, "
            f"пропущено {skipped_count}, всего синхронизировано {synced_count} записей"
        )
        
    except Exception as e:
        logger.error(f"Ошибка периодической синхронизации из YClients: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

