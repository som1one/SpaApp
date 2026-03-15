"""
Схемы Pydantic
"""
from app.schemas.auth import (
    RegisterRequest, LoginRequest, VerifyEmailRequest,
    ResendCodeRequest, TokenResponse, AuthResponse, GoogleLoginRequest
)
from app.schemas.booking import (
    BookingCreate, BookingUpdate, BookingResponse, BookingStatusEnum
)

__all__ = [
    "RegisterRequest", "LoginRequest", "VerifyEmailRequest",
    "ResendCodeRequest", "TokenResponse", "AuthResponse", "GoogleLoginRequest",
    "BookingCreate", "BookingUpdate", "BookingResponse", "BookingStatusEnum"
]

