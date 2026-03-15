"""
Сервис аутентификации - бизнес-логика
"""
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.verification_code import VerificationCode
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.schemas.auth import RegisterRequest, LoginRequest
from app.utils.email import send_verification_code


class AuthService:
    """Сервис для работы с аутентификацией"""
    
    @staticmethod
    def generate_verification_code(length: int = None) -> str:
        """Генерация случайного кода"""
        if length is None:
            length = settings.VERIFICATION_CODE_LENGTH
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    
    @staticmethod
    async def register(db: Session, request: RegisterRequest) -> dict:
        """
        Регистрация нового пользователя
        
        Returns:
            dict: {"user_id": int, "message": str}
        """
        # Проверка существования пользователя
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Доп. проверка длины пароля для bcrypt (72 байта)
        if len(request.password.encode("utf-8")) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароль слишком длинный (максимум 72 байта)"
            )
        
        # Упрощенная регистрация: больше не требуем кода подтверждения.
        # Оставляем проверку уникальности email и валидности пароля,
        # а email сразу считаем подтверждённым.
        hashed_password = get_password_hash(request.password)

        # Генерируем уникальный код пользователя (NOT NULL в БД, нужен для интеграций)
        unique_code = None
        for _ in range(10):  # до 10 попыток найти свободный код
            candidate = secrets.token_urlsafe(6)[:8].upper().replace('-', '').replace('_', '')
            exists = db.query(User).filter(User.unique_code == candidate).first()
            if not exists:
                unique_code = candidate
                break

        user = User(
            name=request.name,
            surname=request.surname,
            email=request.email,
            hashed_password=hashed_password,
            phone=request.phone,
            is_verified=True,
            is_active=True,
            unique_code=unique_code,
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "user_id": user.id,
            "message": "Регистрация завершена"
        }
    
    @staticmethod
    async def request_verification_code(db: Session, email: str) -> dict:
        """
        Больше не отправляем код по email.
        Оставляем только проверку, что пользователя ещё нет, чтобы не плодить дублей.
        Фронт после этого шага сразу может вызывать /register с любым значением code.
        """
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )

        return {"message": "Подтверждение email отключено, можно продолжать регистрацию"}
    
    @staticmethod
    async def login(db: Session, email: str, password: str) -> dict:
        """
        Вход пользователя
        
        Returns:
            dict: {"access_token": str, "refresh_token": str, "token_type": str}
        """
        # Поиск пользователя
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        # Проверка пароля
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        # Проверка активности
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Аккаунт неактивен"
            )
        
        # Создание токенов
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    async def verify_email(db: Session, email: str, code: str) -> dict:
        """
        Подтверждение email
        
        Returns:
            dict: {"message": str}
        """
        # Удаляем просроченные коды для этого email
        from app.utils.timezone import moscow_now
        db.query(VerificationCode).filter(
            VerificationCode.email == email,
            VerificationCode.expires_at < moscow_now()
        ).delete()
        db.commit()
        
        # Поиск кода
        verification_code = db.query(VerificationCode).filter(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.is_used == False
        ).first()
        
        if not verification_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный или истекший код. Пожалуйста, запросите новый код."
            )
        
        # Активация аккаунта
        user = db.query(User).filter(User.id == verification_code.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        user.is_verified = True
        
        # Отмечаем код как использованный
        verification_code.is_used = True
        
        db.commit()
        
        return {"message": "Email успешно подтвержден"}
    
    @staticmethod
    async def resend_code(db: Session, email: str) -> dict:
        """
        Раньше отправляли код повторно на email.
        Сейчас подтверждение email отключено, поэтому просто возвращаем сообщение.
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        return {
            "message": "Подтверждение email отключено, повторная отправка кода не требуется"
        }

