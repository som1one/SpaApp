from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.booking import BookingStatus


class StatusCount(BaseModel):
    status: str
    count: int


class MonthlyBookings(BaseModel):
    month: str
    count: int


class DashboardSummaryResponse(BaseModel):
    total_users: int
    total_bookings: int
    confirmed_bookings: int
    pending_bookings: int
    completed_bookings: int = 0
    cancelled_bookings: int = 0
    status_breakdown: List[StatusCount]
    monthly_bookings: List[MonthlyBookings]


class AdminBookingResponse(BaseModel):
    id: int
    user_id: int
    client_name: Optional[str]
    client_email: Optional[str]
    service_name: str
    appointment_datetime: datetime
    status: str
    phone: Optional[str]
    service_price_cents: Optional[int] = None
    loyalty_bonuses_awarded: Optional[bool] = False
    loyalty_bonuses_amount: Optional[int] = None


class AdminBookingsListResponse(BaseModel):
    items: List[AdminBookingResponse]
    total: int


class BookingUpdateRequest(BaseModel):
    status: BookingStatus
    notes: Optional[str] = None
    service_price_cents: Optional[int] = None
    appointment_datetime: Optional[datetime] = None


class BookingPaymentConfirmationRequest(BaseModel):
    amount_rub: float = Field(..., gt=0)

