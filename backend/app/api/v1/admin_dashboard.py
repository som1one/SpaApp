import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session, joinedload

from app.apis.dependencies import admin_required
from app.core.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.schemas.admin_dashboard import (
    DashboardSummaryResponse,
    AdminBookingsListResponse,
    AdminBookingResponse,
    StatusCount,
    MonthlyBookings,
)
from app.utils.timezone import moscow_now

router = APIRouter(prefix="/admin/dashboard", tags=["Admin Dashboard"])
logger = logging.getLogger(__name__)


@router.get("/summary", response_model=DashboardSummaryResponse)
async def dashboard_summary(
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    try:
        logger.debug("Starting dashboard summary generation")
        
        # Оптимизируем запросы - используем один запрос для подсчёта bookings
        booking_counts = (
            db.query(Booking.status, func.count(Booking.id))
            .group_by(Booking.status)
            .all()
        )
        logger.debug(f"Booking counts query completed: {booking_counts}")
        
        # Извлекаем данные из одного запроса
        total_bookings = sum(count for _, count in booking_counts)
        confirmed = next((count for status, count in booking_counts if status == BookingStatus.CONFIRMED), 0)
        pending = next((count for status, count in booking_counts if status == BookingStatus.PENDING), 0)
        completed = next((count for status, count in booking_counts if status == BookingStatus.COMPLETED), 0)
        cancelled = next((count for status, count in booking_counts if status == BookingStatus.CANCELLED), 0)
        
        status_breakdown = [
            StatusCount(status=status.value if isinstance(status, BookingStatus) else str(status), count=count)
            for status, count in booking_counts
        ]
        logger.debug(f"Status breakdown: {status_breakdown}")

        # Отдельный быстрый запрос для пользователей
        total_users = db.query(func.count(User.id)).scalar() or 0
        logger.debug(f"Total users: {total_users}")
        
        # Месячная статистика
        logger.debug("Getting monthly bookings")
        monthly_breakdown = _get_monthly_bookings(db)
        logger.debug(f"Monthly breakdown: {monthly_breakdown}")

        logger.info(f"Admin summary generated: {total_users} users, {total_bookings} bookings")
        return DashboardSummaryResponse(
            total_users=total_users,
            total_bookings=total_bookings,
            confirmed_bookings=confirmed,
            pending_bookings=pending,
            completed_bookings=completed,
            cancelled_bookings=cancelled,
            status_breakdown=status_breakdown,
            monthly_bookings=monthly_breakdown,
        )
    except Exception as e:
        logger.error(f"Error generating dashboard summary: {e}", exc_info=True)
        # Возвращаем пустые данные вместо ошибки, чтобы фронтенд не падал
        return DashboardSummaryResponse(
            total_users=0,
            total_bookings=0,
            confirmed_bookings=0,
            pending_bookings=0,
            completed_bookings=0,
            cancelled_bookings=0,
            status_breakdown=[],
            monthly_bookings=[],
        )


@router.get("/bookings", response_model=AdminBookingsListResponse)
async def dashboard_bookings(
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: BookingStatus | None = Query(None),
):
    try:
        # Сначала считаем общее количество без joinedload (для правильного count)
        count_query = db.query(Booking)
        if status:
            count_query = count_query.filter(Booking.status == status)
        total = count_query.count()
        
        # Затем загружаем данные с joinedload для избежания N+1 проблем
        query = db.query(Booking).options(joinedload(Booking.user)).order_by(Booking.appointment_datetime.desc())
        if status:
            query = query.filter(Booking.status == status)
        
        items = query.offset(offset).limit(limit).all()

        response_items = []
        for booking in items:
            try:
                # Безопасное получение данных пользователя
                user = booking.user if hasattr(booking, 'user') else None
                # Проверяем, что appointment_datetime не None (хотя по модели он обязательный)
                if booking.appointment_datetime is None:
                    logger.warning(f"Booking {booking.id} has null appointment_datetime")
                    continue
                    
                response_items.append(
                    AdminBookingResponse(
                        id=booking.id,
                        user_id=booking.user_id or 0,
                        client_name=getattr(user, "name", None) if user else None,
                        client_email=getattr(user, "email", None) if user else None,
                        service_name=booking.service_name or "Услуга",
                        appointment_datetime=booking.appointment_datetime,
                        status=booking.status.value if hasattr(booking.status, 'value') else str(booking.status),
                        phone=booking.phone,
                    )
                )
            except Exception as e:
                logger.warning(f"Error processing booking {booking.id}: {e}")
                continue

        return AdminBookingsListResponse(items=response_items, total=total)
    except Exception as e:
        logger.error(f"Error in dashboard_bookings: {e}", exc_info=True)
        # Возвращаем пустой список при ошибке
        return AdminBookingsListResponse(items=[], total=0)


def _month_floor(dt: datetime) -> datetime:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _subtract_months(dt: datetime, months: int) -> datetime:
    year = dt.year
    month = dt.month - months
    while month <= 0:
        month += 12
        year -= 1
    return dt.replace(year=year, month=month)


def _get_monthly_bookings(db: Session) -> list[MonthlyBookings]:
    try:
        now = moscow_now()
        start = _subtract_months(_month_floor(now), 5)

        # Используем raw SQL для надежной работы с PostgreSQL date_trunc
        # Это гарантированно работает на всех версиях PostgreSQL
        # Используем имя таблицы из модели (безопасно, так как берется из модели)
        table_name = Booking.__tablename__
        # Используем format для подстановки имени таблицы (безопасно, так как это константа из модели)
        sql_query = text("""
            SELECT 
                DATE_TRUNC('month', appointment_datetime)::date as month,
                COUNT(*) as count
            FROM {} 
            WHERE appointment_datetime >= :start_date
            GROUP BY DATE_TRUNC('month', appointment_datetime)
            ORDER BY month
        """.format(table_name))
        
        result = db.execute(sql_query, {"start_date": start})
        rows = result.fetchall()

        # Обрабатываем результаты
        counts_map = {}
        for row in rows:
            month_date = row[0]  # Первый столбец - дата месяца
            count = row[1]  # Второй столбец - количество
            if month_date:
                month_key = month_date.strftime("%Y-%m")
                counts_map[month_key] = count

        # Формируем список месяцев
        months = []
        for i in range(5, -1, -1):
            current = _subtract_months(_month_floor(now), i)
            key = current.strftime("%Y-%m")
            months.append(MonthlyBookings(month=key, count=counts_map.get(key, 0)))

        return months
    except Exception as e:
        logger.error(f"Error in _get_monthly_bookings: {e}", exc_info=True)
        # Возвращаем пустой список при ошибке
        return []


