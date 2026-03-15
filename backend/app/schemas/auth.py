"""
Pydantic схемы для аутентификации
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional


class RegisterRequest(BaseModel):
    """Схема для регистрации"""
    name: str = Field(..., min_length=2, max_length=100)
    surname: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    # bcrypt ограничивает пароль 72 байтами, поэтому ставим потолок 72 символа
    password: str = Field(..., min_length=6, max_length=72)
    phone: str = Field(..., min_length=4, max_length=20)
    code: str = Field(..., min_length=6, max_length=6)

    @validator('phone')
    def validate_phone(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError('Телефон обязателен')
        if not cleaned.startswith('+'):
            cleaned = f'+{cleaned}'
        digits = cleaned.replace('+', '')
        if not digits.isdigit():
            raise ValueError('Телефон должен содержать только цифры и +')
        return cleaned


class LoginRequest(BaseModel):
    """Схема для входа"""
    email: EmailStr
    password: str


class VerifyEmailRequest(BaseModel):
    """Схема для подтверждения email"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


class ResendCodeRequest(BaseModel):
    """Схема для повторной отправки кода"""
    email: EmailStr


class RequestCodeRequest(BaseModel):
    """Схема для запроса кода регистрации"""
    email: EmailStr
    phone: str | None = None


class TokenResponse(BaseModel):
    """Ответ с токеном"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """Ответ после успешной операции"""
    success: bool = True
    message: str
    user_id: Optional[int] = None
    code: Optional[str] = None  # Код подтверждения (для разработки)


class GoogleLoginRequest(BaseModel):
    """Схема для входа через Google"""
    id_token: str
    email: str
    name: Optional[str] = None
    photo_url: Optional[str] = None


class VkLoginRequest(BaseModel):
    """Схема для входа через VK ID"""
    access_token: str
    user_id: int
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None


