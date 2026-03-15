"""
API endpoints для нового booking flow с YClients
"""
import logging
from typing import Optional, List
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.services.yclients_service import yclients_service
from app.models.service import Service
from app.models.user import User
from app.models.staff import Staff, StaffSchedule, StaffService, DayOfWeek

router = APIRouter(prefix="/booking", tags=["Booking"])
logger = logging.getLogger(__name__)


async def _generate_slots_from_staff_schedule(
    db: Session,
    staff_id: int,
    service: Service,
    target_date: date,
) -> List['TimeSlot']:
    """Генерация временных слотов из расписания мастера"""
    logger.info(f"Генерация слотов для staff_id={staff_id}, date={target_date}")
    
    # Получаем мастера
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        return []
    
    # Определяем день недели (0 = Monday, 6 = Sunday)
    day_of_week_value = target_date.weekday()
    
    # Получаем расписание на этот день
    schedule = db.query(StaffSchedule).filter(
        StaffSchedule.staff_id == staff_id,
        StaffSchedule.day_of_week == day_of_week_value,
        StaffSchedule.is_active == True,
    ).first()
    
    if not schedule:
        logger.info(f"Нет расписания для staff_id={staff_id} на день {day_of_week_value}")
        return []
    
    # Генерируем слоты с интервалом 30 минут
    slots = []
    duration = service.duration if service.duration else 60  # По умолчанию 60 минут
    slot_interval = 30  # Интервал между слотами - 30 минут
    
    # Начальное время
    current_time = datetime.combine(target_date, schedule.start_time)
    end_time = datetime.combine(target_date, schedule.end_time)
    
    logger.info(f"Расписание: {schedule.start_time} - {schedule.end_time}, duration={duration}мин")
    
    # Проверяем корректность времени
    if current_time >= end_time:
        logger.warning(f"Некорректное расписание: время начала >= времени окончания")
        return []
    
    while current_time + timedelta(minutes=duration) <= end_time:
        # Проверяем, не попадает ли слот в перерыв
        if schedule.break_start and schedule.break_end:
            break_start = datetime.combine(target_date, schedule.break_start)
            break_end = datetime.combine(target_date, schedule.break_end)
            
            # Пропускаем слот, если он попадает в перерыв
            if not (current_time + timedelta(minutes=duration) <= break_start or current_time >= break_end):
                current_time += timedelta(minutes=slot_interval)
                continue
        
        # Проверяем, не прошло ли уже это время (для сегодняшнего дня)
        from app.utils.timezone import moscow_now
        if target_date == date.today() and current_time <= moscow_now().time():
            current_time += timedelta(minutes=slot_interval)
            continue
        
        # Добавляем слот
        time_str = current_time.strftime("%H:%M")
        date_str = target_date.strftime("%Y-%m-%d")
        
        slots.append(TimeSlot(
            date=date_str,
            time=time_str,
            datetime=f"{date_str} {time_str}",
            available=True,
        ))
        
        current_time += timedelta(minutes=slot_interval)
    
    logger.info(f"Сгенерировано {len(slots)} слотов для {target_date}")
    return slots


class StaffMember(BaseModel):
    """Мастер из YClients"""
    id: int
    name: str
    specialization: Optional[str] = None
    avatar: Optional[str] = None
    rating: Optional[float] = None


class TimeSlot(BaseModel):
    """Временной слот"""
    date: str
    time: str
    datetime: str
    available: bool = True


class BookingRequest(BaseModel):
    """Запрос на создание записи"""
    service_id: int = Field(..., description="ID услуги в нашей БД")
    staff_id: int = Field(..., description="ID мастера в YClients")
    datetime_str: str = Field(..., description="Дата и время в формате YYYY-MM-DD HH:MM")
    use_bonuses: bool = Field(False, description="Использовать бонусы")
    bonuses_amount: int = Field(0, description="Количество бонусов к списанию", ge=0)
    comment: Optional[str] = Field(None, description="Комментарий к записи")


class BookingResponse(BaseModel):
    """Ответ после создания записи"""
    success: bool
    booking_id: Optional[int] = None
    message: str
    bonuses_used: int = 0
    final_price: float = 0


@router.get("/staff/{service_id}", response_model=List[StaffMember])
async def get_available_staff(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить список доступных мастеров для услуги из нашей БД
    
    Args:
        service_id: ID услуги в нашей БД
    
    Returns:
        Список мастеров
    """
    # Получаем услугу
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена"
        )
    
    # Получаем мастеров, которые могут выполнять эту услугу
    # Если есть привязки в staff_services - берем только их
    # Иначе возвращаем всех активных мастеров
    staff_services = (
        db.query(StaffService)
        .filter(
            StaffService.service_id == service_id,
            StaffService.is_active == True
        )
        .all()
    )
    
    if staff_services:
        # Есть конкретные привязки
        staff_ids = [ss.staff_id for ss in staff_services]
        staff_list = (
            db.query(Staff)
            .filter(
                Staff.id.in_(staff_ids),
                Staff.is_active == True
            )
            .order_by(Staff.order_index.asc(), Staff.name.asc())
            .all()
        )
    else:
        # Нет привязок - возвращаем всех активных мастеров
        staff_list = (
            db.query(Staff)
            .filter(Staff.is_active == True)
            .order_by(Staff.order_index.asc(), Staff.name.asc())
            .all()
        )
    
    if not staff_list:
        # Если мастеров нет в БД, пытаемся загрузить из YClients (fallback)
        if settings.YCLIENTS_ENABLED and settings.YCLIENTS_COMPANY_ID:
            yclients_service.configure(
                company_id=settings.YCLIENTS_COMPANY_ID,
                api_token=settings.YCLIENTS_API_TOKEN,
                user_token=settings.YCLIENTS_USER_TOKEN,
            )
            try:
                all_staff = await yclients_service.get_staff()
                # Фильтруем и форматируем
                yclients_staff_list = []
                for staff_member in all_staff:
                    # Если услуга привязана к конкретному мастеру
                    if service.yclients_staff_id and staff_member.get("id") != service.yclients_staff_id:
                        continue
                    
                    yclients_staff_list.append(StaffMember(
                        id=staff_member.get("id"),
                        name=staff_member.get("name", "Мастер"),
                        specialization=staff_member.get("specialization"),
                        avatar=staff_member.get("avatar"),
                        rating=staff_member.get("rating"),
                    ))
                
                if not yclients_staff_list:
                    logger.warning(f"Нет доступных мастеров для услуги {service_id}")
                
                return yclients_staff_list
            except Exception as e:
                logger.error(f"Ошибка получения мастеров из YClients: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка получения списка мастеров: {str(e)}"
                )
        else:
            # YClients отключен и мастеров в БД нет
            logger.warning(f"Нет мастеров для услуги {service_id}")
            return []
    
    # Форматируем мастеров из БД
    result = []
    for staff in staff_list:
        # Используем yclients_staff_id если есть, иначе используем наш внутренний ID
        staff_id_to_use = staff.yclients_staff_id if staff.yclients_staff_id else staff.id
        
        full_name = f"{staff.name} {staff.surname or ''}".strip()
        
        result.append(StaffMember(
            id=staff_id_to_use,
            name=full_name,
            specialization=staff.specialization,
            avatar=staff.photo_url,
            rating=None,  # Рейтинг можно добавить позже
        ))
    
    return result


@router.get("/available-days/{service_id}")
async def get_available_days(
    service_id: int,
    staff_id: int = Query(..., description="ID мастера из нашей БД (Staff.id)"),
    days_ahead: int = Query(60, description="Количество дней вперед для проверки"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить список доступных дней для записи
    
    Args:
        service_id: ID услуги в нашей БД
        staff_id: ID мастера из нашей БД (Staff.id)
        days_ahead: Количество дней вперед для проверки (по умолчанию 60)
    
    Returns:
        Список доступных дат в формате ["YYYY-MM-DD", ...]
    """
    # Получаем услугу
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена"
        )
    
    # Получаем мастера
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мастер не найден"
        )
    
    # Проверяем, можно ли использовать YClients
    use_yclients = (
        settings.YCLIENTS_ENABLED
        and service.yclients_service_id is not None
        and staff.yclients_staff_id is not None
    )
    
    if use_yclients:
        # Настраиваем YClients
        if settings.YCLIENTS_COMPANY_ID:
            yclients_service.configure(
                company_id=settings.YCLIENTS_COMPANY_ID,
                api_token=settings.YCLIENTS_API_TOKEN,
                user_token=settings.YCLIENTS_USER_TOKEN,
            )
        
        try:
            # Получаем доступные даты из YClients
            available_dates = await yclients_service.get_available_dates(
                service_id=service.yclients_service_id,
                staff_id=staff.yclients_staff_id,
                date_from=date.today(),
                date_to=date.today() + timedelta(days=days_ahead),
            )
            
            # Извлекаем только даты, у которых есть слоты
            result = []
            for date_info in available_dates:
                date_val = date_info.get("date", "")
                times = date_info.get("times", [])
                if date_val and times and len(times) > 0:
                    result.append(date_val)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения доступных дней из YClients: {e}", exc_info=True)
            # Fallback на локальное расписание
            use_yclients = False
    
    # Используем локальное расписание
    if not use_yclients:
        result = []
        today = date.today()
        
        # Получаем расписание мастера
        schedules = db.query(StaffSchedule).filter(
            StaffSchedule.staff_id == staff_id,
            StaffSchedule.is_active == True,
        ).all()
        
        if not schedules:
            return result
        
        # Проверяем каждый день в диапазоне
        for day_offset in range(days_ahead):
            check_date = today + timedelta(days=day_offset)
            day_of_week = check_date.weekday()
            
            # Ищем расписание на этот день недели
            schedule = next(
                (s for s in schedules if s.day_of_week == day_of_week),
                None
            )
            
            if schedule:
                # Проверяем, не прошло ли уже время (для сегодняшнего дня)
                if check_date == today:
                    from app.utils.timezone import moscow_now
                    current_time = moscow_now().time()
                    if current_time < schedule.end_time:
                        result.append(check_date.strftime("%Y-%m-%d"))
                else:
                    result.append(check_date.strftime("%Y-%m-%d"))
        
        return result


@router.get("/time-slots/{service_id}", response_model=List[TimeSlot])
async def get_available_time_slots(
    service_id: int,
    staff_id: int = Query(..., description="ID мастера из нашей БД (Staff.id)"),
    date_str: Optional[str] = Query(None, description="Дата в формате YYYY-MM-DD (по умолчанию сегодня)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить доступные временные слоты для записи
    
    Args:
        service_id: ID услуги в нашей БД
        staff_id: ID мастера из нашей БД (Staff.id)
        date_str: Дата в формате YYYY-MM-DD
    
    Returns:
        Список доступных временных слотов
    """
    # Получаем услугу
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена"
        )
    
    # Определяем дату
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат даты. Используйте YYYY-MM-DD"
            )
    else:
        target_date = date.today()
    
    # Проверяем, можно ли использовать YClients
    use_yclients = (
        settings.YCLIENTS_ENABLED
        and service.yclients_service_id is not None
    )
    
    # Если YClients отключен или услуга не привязана, используем локальное расписание
    if not use_yclients:
        logger.info(f"Используем локальное расписание для service_id={service_id} (YClients: {settings.YCLIENTS_ENABLED}, yclients_service_id: {service.yclients_service_id})")
        return await _generate_slots_from_staff_schedule(
            db=db,
            staff_id=staff_id,
            service=service,
            target_date=target_date,
        )
    
    # Получаем мастера из БД для YClients staff_id
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мастер не найден"
        )
    
    # Если мастер не привязан к YClients, используем локальное расписание
    if not staff.yclients_staff_id:
        logger.info(f"Мастер {staff_id} не привязан к YClients, используем локальное расписание")
        return await _generate_slots_from_staff_schedule(
            db=db,
            staff_id=staff_id,
            service=service,
            target_date=target_date,
        )
    
    # Настраиваем YClients
    if settings.YCLIENTS_COMPANY_ID:
        yclients_service.configure(
            company_id=settings.YCLIENTS_COMPANY_ID,
            api_token=settings.YCLIENTS_API_TOKEN,
            user_token=settings.YCLIENTS_USER_TOKEN,
        )
    
    try:
        # Получаем доступные слоты из YClients
        available_dates = await yclients_service.get_available_dates(
            service_id=service.yclients_service_id,
            staff_id=staff.yclients_staff_id,  # Используем YClients staff ID
            date_from=target_date,
            date_to=target_date + timedelta(days=14),  # +2 недели
        )
        
        # Форматируем в удобный вид
        time_slots = []
        for date_info in available_dates:
            date_val = date_info.get("date", "")
            times = date_info.get("times", [])
            
            for time_val in times:
                if isinstance(time_val, str):
                    time_slots.append(TimeSlot(
                        date=date_val,
                        time=time_val,
                        datetime=f"{date_val} {time_val}",
                        available=True,
                    ))
        
        return time_slots
        
    except Exception as e:
        logger.error(f"Ошибка получения слотов: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения доступных слотов: {str(e)}"
        )


@router.post("/create", response_model=BookingResponse)
async def create_booking(
    booking: BookingRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создать запись с возможностью использования бонусов
    
    Args:
        booking: Данные для создания записи
    
    Returns:
        Результат создания записи
    """
    if not settings.YCLIENTS_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YClients интеграция отключена"
        )
    
    # Настраиваем YClients
    if settings.YCLIENTS_COMPANY_ID:
        yclients_service.configure(
            company_id=settings.YCLIENTS_COMPANY_ID,
            api_token=settings.YCLIENTS_API_TOKEN,
            user_token=settings.YCLIENTS_USER_TOKEN,
        )
    
    # Получаем услугу
    service = db.query(Service).filter(Service.id == booking.service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена"
        )
    
    # Проверяем, привязана ли услуга к YClients
    use_yclients = service.yclients_service_id is not None
    
    # Если услуга не привязана, пытаемся найти её в YClients по имени
    if not use_yclients:
        logger.info(
            f"Услуга {service.id} ({service.name}) не привязана к YClients. "
            f"Пытаемся найти в YClients по имени..."
        )
        
        try:
            yc_services = await yclients_service.get_services()
            if yc_services:
                # Нормализуем имя услуги для поиска
                service_name_normalized = service.name.lower().strip()
                # Убираем лишние пробелы и приводим к единому формату
                service_name_normalized = ' '.join(service_name_normalized.split())
                
                matching_service = None
                best_match_score = 0
                
                # Стратегия 1: Точное совпадение (без учета регистра)
                for yc_service in yc_services:
                    yc_name = yc_service.get('title', '').lower().strip()
                    yc_name = ' '.join(yc_name.split())
                    
                    if yc_name == service_name_normalized:
                        matching_service = yc_service
                        best_match_score = 100
                        break
                
                # Стратегия 2: Частичное совпадение (если точное не найдено)
                if not matching_service:
                    for yc_service in yc_services:
                        yc_name = yc_service.get('title', '').lower().strip()
                        yc_name = ' '.join(yc_name.split())
                        
                        # Проверяем, содержит ли одно название другое
                        if service_name_normalized in yc_name or yc_name in service_name_normalized:
                            # Вычисляем процент совпадения
                            longer = max(len(service_name_normalized), len(yc_name))
                            shorter = min(len(service_name_normalized), len(yc_name))
                            if longer > 0:
                                match_score = (shorter / longer) * 100
                                if match_score > best_match_score and match_score >= 70:  # Минимум 70% совпадения
                                    matching_service = yc_service
                                    best_match_score = match_score
                
                # Стратегия 3: Поиск по ключевым словам (если предыдущие не сработали)
                if not matching_service:
                    # Извлекаем ключевые слова из названия услуги
                    service_keywords = set(service_name_normalized.split())
                    service_keywords = {w for w in service_keywords if len(w) > 3}  # Только слова длиннее 3 символов
                    
                    for yc_service in yc_services:
                        yc_name = yc_service.get('title', '').lower().strip()
                        yc_name = ' '.join(yc_name.split())
                        yc_keywords = set(yc_name.split())
                        yc_keywords = {w for w in yc_keywords if len(w) > 3}
                        
                        # Считаем количество совпадающих ключевых слов
                        common_keywords = service_keywords & yc_keywords
                        if common_keywords:
                            match_score = (len(common_keywords) / max(len(service_keywords), len(yc_keywords))) * 100
                            if match_score > best_match_score and match_score >= 50:  # Минимум 50% совпадения ключевых слов
                                matching_service = yc_service
                                best_match_score = match_score
                
                if matching_service:
                    yc_service_id = matching_service.get('id')
                    if yc_service_id:
                        # Привязываем услугу к YClients
                        service.yclients_service_id = yc_service_id
                        db.commit()
                        db.refresh(service)
                        use_yclients = True
                        logger.info(
                            f"✅ Услуга {service.id} '{service.name}' автоматически привязана к YClients "
                            f"(ID: {yc_service_id}, совпадение: {best_match_score:.1f}%, "
                            f"YClients название: '{matching_service.get('title')}')"
                        )
                    else:
                        logger.warning(
                            f"Найдена услуга '{matching_service.get('title')}' в YClients, "
                            f"но у неё нет ID"
                        )
                else:
                    # Показываем топ-5 наиболее похожих услуг для отладки
                    similar_services = []
                    service_words = set(service_name_normalized.split())
                    
                    for yc_service in yc_services[:20]:  # Проверяем первые 20 для производительности
                        yc_name = yc_service.get('title', '').lower().strip()
                        yc_words = set(yc_name.split())
                        common = service_words & yc_words
                        if common:
                            similarity = len(common) / max(len(service_words), len(yc_words))
                            similar_services.append((similarity, yc_service.get('title')))
                    
                    similar_services.sort(reverse=True)
                    top_similar = [name for _, name in similar_services[:5]]
                    
                    logger.warning(
                        f"Услуга '{service.name}' не найдена в YClients. "
                        f"Наиболее похожие: {top_similar}"
                    )
            else:
                logger.warning("Не удалось получить список услуг из YClients")
        except Exception as e:
            logger.error(
                f"Ошибка при поиске услуги в YClients: {e}",
                exc_info=True
            )
    
    if not use_yclients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Услуга не найдена в YClients",
                "service_id": service.id,
                "service_name": service.name,
                "solution": "Запустите синхронизацию: python scripts/sync_yclients_catalog.py",
                "message": f"Услуга '{service.name}' не привязана к YClients и не найдена автоматически. "
                          f"Пожалуйста, синхронизируйте услуги или обратитесь к администратору."
            }
        )
    
    # Проверяем и применяем бонусы
    bonuses_to_use = 0
    final_price = service.price or 0
    
    if booking.use_bonuses and booking.bonuses_amount > 0:
        # Проверяем, что у пользователя достаточно бонусов
        user_bonuses = current_user.loyalty_bonuses or 0
        
        if booking.bonuses_amount > user_bonuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недостаточно бонусов. Доступно: {user_bonuses}"
            )
        
        # 1 бонус = 1 рубль
        bonuses_to_use = min(booking.bonuses_amount, int(final_price))
        final_price = final_price - bonuses_to_use
        
        logger.info(f"Применяем {bonuses_to_use} бонусов, итоговая цена: {final_price}")
    
    # Формируем комментарий
    comment_parts = []
    if booking.comment:
        comment_parts.append(booking.comment)
    
    if bonuses_to_use > 0:
        comment_parts.append(f"💎 Списано {bonuses_to_use} бонусов (скидка {bonuses_to_use} ₽)")
        comment_parts.append(f"К оплате: {final_price:.0f} ₽")
    
    full_comment = " | ".join(comment_parts) if comment_parts else None
    
    # Формируем имя клиента
    client_name = f"{current_user.name or ''} {current_user.surname or ''}".strip()
    if not client_name:
        client_name = current_user.email
    
    try:
        # Создаем запись в YClients (теперь use_yclients всегда True после проверки выше)
        result = await yclients_service.create_booking(
            service_id=service.yclients_service_id,
            datetime_str=booking.datetime_str,
            client_name=client_name,
            client_phone=current_user.phone or "",
            client_email=current_user.email,
            staff_id=booking.staff_id,
            comment=full_comment,
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось создать запись в YClients"
            )
        
        yclients_record_id = result.get("id")
        booking_notes = f"YClients. ID: {yclients_record_id}"
        if full_comment:
            booking_notes = f"{full_comment} | {booking_notes}"
        
        logger.info(
            f"✅ Запись создана в YClients: ID={yclients_record_id}, "
            f"услуга={service.name}, пользователь={current_user.id}"
        )
        
        # Списываем бонусы если они использовались
        if bonuses_to_use > 0:
            current_user.loyalty_bonuses = (current_user.loyalty_bonuses or 0) - bonuses_to_use
            current_user.spent_bonuses = (current_user.spent_bonuses or 0) + bonuses_to_use
            db.commit()
            logger.info(f"Списано {bonuses_to_use} бонусов у пользователя {current_user.id}, потрачено всего: {current_user.spent_bonuses}")
        
        # Создаем запись в локальной БД
        from datetime import datetime as dt
        from app.models.booking import Booking, BookingStatus
        
        appointment_dt = dt.fromisoformat(booking.datetime_str.replace('Z', '+00:00'))
        
        local_booking = Booking(
            user_id=current_user.id,
            service_name=service.name,
            service_duration=service.duration,
            service_price=int(final_price * 100) if final_price else None,  # Конвертируем в копейки
            appointment_datetime=appointment_dt,
            status=BookingStatus.PENDING,
            notes=booking_notes,
            phone=current_user.phone or current_user.email,
        )
        
        db.add(local_booking)
        db.commit()
        db.refresh(local_booking)
        
        logger.info(
            f"Бронирование создано: локальное ID={local_booking.id}, "
            f"YClients ID={yclients_record_id}, пользователь={current_user.id}"
        )
        
        return BookingResponse(
            success=True,
            booking_id=yclients_record_id or local_booking.id,
            message="Запись успешно создана в YClients",
            bonuses_used=bonuses_to_use,
            final_price=final_price,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания записи: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания записи: {str(e)}"
        )

