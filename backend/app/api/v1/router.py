"""
Главный роутер API v1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, bookings, services
from app.api.v1 import admin_auth, admin_dashboard, admin_menu, admin_users, admin_bookings, admin_audit, admin_notifications, devices, menu_public, loyalty_public, admin_loyalty, yclients, booking, admin_staff, admin_custom_content, custom_content_public

api_router = APIRouter()

# Подключаем все endpoints
api_router.include_router(
    auth.router,
    tags=["Authentication"]
)

api_router.include_router(
    bookings.router,
    tags=["Bookings"]
)

api_router.include_router(
    services.router,
    tags=["Services"]
)

api_router.include_router(
    admin_auth.router,
    tags=["Admin Auth"]
)

api_router.include_router(
    admin_dashboard.router,
    tags=["Admin Dashboard"]
)

api_router.include_router(
    admin_users.router,
    tags=["Admin Users"]
)

api_router.include_router(
    admin_menu.router,
    tags=["Admin Menu"]
)

api_router.include_router(
    admin_bookings.router,
    tags=["Admin Bookings"]
)

api_router.include_router(
    admin_audit.router,
    tags=["Admin Audit"]
)

api_router.include_router(
    admin_notifications.router,
    tags=["Admin Notifications"]
)

api_router.include_router(
    devices.router,
    tags=["Devices"]
)

api_router.include_router(
    menu_public.router,
    tags=["Menu"]
)

api_router.include_router(
    loyalty_public.router,
    tags=["Loyalty"]
)

api_router.include_router(
    admin_loyalty.router,
    tags=["Admin Loyalty"]
)

api_router.include_router(
    yclients.router,
    tags=["YClients"]
)

api_router.include_router(
    booking.router,
    tags=["Booking"]
)

api_router.include_router(
    admin_staff.router,
    tags=["Admin Staff"]
)

api_router.include_router(
    admin_custom_content.router,
    tags=["Admin Custom Content"]
)

api_router.include_router(
    custom_content_public.router,
    tags=["Custom Content"]
)

