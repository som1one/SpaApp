"""
API endpoints для аутентификации
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.schemas.auth import (
    RegisterRequest, LoginRequest, VerifyEmailRequest,
    ResendCodeRequest, TokenResponse, AuthResponse, GoogleLoginRequest,
    VkLoginRequest, RequestCodeRequest, UserUpdateRequest
)
from app.services.auth_service import AuthService
from app.services.storage_service import StorageService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
optional_bearer = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    logger.info("Запрос регистрации", extra={"email": request.email})
    result = await AuthService.register(db, request)
    return AuthResponse(
        success=True,
        message=result["message"],
        user_id=result["user_id"],
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Вход пользователя"""
    logger.info("Запрос логина", extra={"email": request.email})
    return await AuthService.login(db, request.email, request.password)


@router.post("/verify-email", response_model=AuthResponse)
async def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Подтверждение email адреса"""
    logger.info("Подтверждение email", extra={"email": request.email})
    result = await AuthService.verify_email(db, request.email, request.code)
    return AuthResponse(success=True, message=result["message"])


@router.post("/request-code", response_model=AuthResponse)
async def request_code(
    request: RequestCodeRequest,
    db: Session = Depends(get_db)
):
    """Отправка кода для новой регистрации"""
    logger.info("Запрос кода регистрации", extra={"email": request.email})
    result = await AuthService.request_verification_code(db, request.email)
    return AuthResponse(success=True, message=result["message"])


@router.post("/resend-code", response_model=AuthResponse)
async def resend_code(
    request: ResendCodeRequest,
    db: Session = Depends(get_db)
):
    """Повторная отправка кода подтверждения"""
    logger.info("Повторная отправка кода", extra={"email": request.email})
    result = await AuthService.resend_code(db, request.email)
    return AuthResponse(success=True, message=result["message"])


@router.get("/check-email")
async def check_email(email: str, phone: str | None = None, db: Session = Depends(get_db)):
    """Проверка существования пользователя с указанным email"""
    logger.info("Проверка email", extra={"email": email, "phone": phone})
    user = db.query(User).filter(User.email == email).first()
    logger.info(
        "Результат проверки email",
        extra={"email": email, "exists": user is not None}
    )

    if not user and phone:
        logger.debug("Новый email, телефон передан", extra={"email": email, "phone": phone})
    return {"exists": user is not None, "phone": phone}


@router.post("/google", response_model=TokenResponse)
async def google_login(
    request: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """Вход через Google"""
    logger.info("Google Sign-In старт", extra={"email": request.email})
    try:
        from google.auth.transport import requests
        from google.oauth2 import id_token as google_id_token

        CLIENT_ID = settings.GOOGLE_CLIENT_ID
        if not CLIENT_ID:
            logger.error("Google Client ID не настроен")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google Client ID не настроен"
            )

        try:
            idinfo = google_id_token.verify_oauth2_token(
                request.id_token,
                requests.Request(),
                CLIENT_ID
            )
            logger.debug("Google токен верифицирован", extra={"email": idinfo.get("email")})

            if idinfo.get('email') != request.email:
                logger.warning(
                    "Email из токена не совпадает",
                    extra={"token_email": idinfo.get('email'), "request_email": request.email}
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email не совпадает с токеном"
                )
        except ValueError as e:
            logger.error("Неверный Google token", extra={"error": str(e)})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Неверный Google token: {str(e)}"
            )

        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            logger.info("Создание пользователя из Google", extra={"email": request.email})
            name_parts = (request.name or "User").split(maxsplit=1)
            name = name_parts[0] if name_parts else "User"
            surname = name_parts[1] if len(name_parts) > 1 else ""

            user = User(
                email=request.email,
                name=name,
                surname=surname,
                is_verified=True,
                is_active=True,
                avatar_url=request.photo_url
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            logger.info("Обновление пользователя", extra={"email": request.email})
            if request.name:
                name_parts = request.name.split(maxsplit=1)
                if not user.name:
                    user.name = name_parts[0] if name_parts else "User"
                if not user.surname and len(name_parts) > 1:
                    user.surname = name_parts[1]

            if request.photo_url and not user.avatar_url:
                user.avatar_url = request.photo_url

            user.is_verified = True
            db.commit()

        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        logger.info("Google Sign-In успешен", extra={"email": request.email, "user_id": user.id})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Ошибка при Google авторизации", extra={"email": request.email})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке Google авторизации: {str(e)}"
        )


@router.post("/vk", response_model=TokenResponse)
async def vk_login(
    request: VkLoginRequest,
    db: Session = Depends(get_db)
):
    """Вход через VK ID"""
    logger.info("VK ID Sign-In старт", extra={"user_id": request.user_id, "email": request.email})
    try:
        import httpx
        
        VK_APP_ID = settings.VK_APP_ID
        VK_SECRET_KEY = settings.VK_SECRET_KEY
        
        if not VK_APP_ID or not VK_SECRET_KEY:
            logger.error("VK App ID или Secret Key не настроены")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="VK App ID или Secret Key не настроены"
            )
        
        # Проверяем токен VK через API
        async with httpx.AsyncClient() as client:
            verify_response = await client.get(
                "https://api.vk.com/method/users.get",
                params={
                    "access_token": request.access_token,
                    "user_ids": request.user_id,
                    "fields": "photo_200",
                    "v": "5.131"
                },
                timeout=10.0
            )
            
            if verify_response.status_code != 200:
                logger.error("Ошибка проверки VK токена", extra={"status": verify_response.status_code})
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Не удалось проверить VK токен"
                )
            
            vk_data = verify_response.json()
            if "error" in vk_data:
                logger.error("VK API вернул ошибку", extra={"error": vk_data["error"]})
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Неверный VK токен: {vk_data['error'].get('error_msg', 'Unknown error')}"
                )
            
            vk_users = vk_data.get("response", [])
            if not vk_users or vk_users[0].get("id") != request.user_id:
                logger.warning("User ID из токена не совпадает", extra={"vk_id": vk_users[0].get("id") if vk_users else None, "request_id": request.user_id})
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID не совпадает с токеном"
                )
            
            vk_user = vk_users[0]
            logger.debug("VK токен верифицирован", extra={"user_id": vk_user.get("id")})
        
        # Ищем или создаем пользователя
        # Используем email если есть, иначе создаем временный email на основе VK ID
        email = request.email
        if not email:
            # Если email не предоставлен, создаем временный
            email = f"vk_{request.user_id}@vk.temp"
            logger.info("Email не предоставлен VK, используем временный", extra={"user_id": request.user_id})
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.info("Создание пользователя из VK", extra={"email": email, "vk_id": request.user_id})
            name = request.first_name or vk_user.get("first_name", "User")
            surname = request.last_name or vk_user.get("last_name", "")
            photo_url = request.photo_url or vk_user.get("photo_200")
            
            user = User(
                email=email,
                name=name,
                surname=surname,
                is_verified=True,  # VK пользователи считаются верифицированными
                is_active=True,
                avatar_url=photo_url
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            logger.info("Обновление пользователя из VK", extra={"email": email})
            # Обновляем данные если они отсутствуют
            if request.first_name and not user.name:
                user.name = request.first_name
            elif vk_user.get("first_name") and not user.name:
                user.name = vk_user.get("first_name")
            
            if request.last_name and not user.surname:
                user.surname = request.last_name
            elif vk_user.get("last_name") and not user.surname:
                user.surname = vk_user.get("last_name")
            
            if (request.photo_url or vk_user.get("photo_200")) and not user.avatar_url:
                user.avatar_url = request.photo_url or vk_user.get("photo_200")
            
            user.is_verified = True
            db.commit()
        
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        logger.info("VK ID Sign-In успешен", extra={"email": email, "user_id": user.id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Ошибка при VK авторизации", extra={"user_id": request.user_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке VK авторизации: {str(e)}"
        )


@router.get("/me")
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer),
    db: Session = Depends(get_db),
):
    """
    Получить информацию о текущем пользователе.

    Если токен не передан или невалиден — возвращаем "гостя", но без 401.
    """
    guest = {
        "id": 0,
        "name": "Гость",
        "surname": "",
        "email": "",
        "phone": None,
        "is_verified": False,
        "avatar_url": None,
        "loyalty_level": 1,
        "auto_apply_loyalty_points": False,
        "is_authenticated": False,
    }

    if credentials is None:
        logger.debug("Запрос профиля без токена, возвращаем гостя")
        return guest

    token = credentials.credentials
    payload = decode_token(token)
    if payload is None or "sub" not in payload:
        logger.debug("Невалидный токен в /me, возвращаем гостя")
        return guest

    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.debug("Пользователь не найден по токену в /me, возвращаем гостя", extra={"user_id": user_id})
        return guest

    logger.debug("Запрос профиля", extra={"user_id": user.id})
    return {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "phone": user.phone,
        "is_verified": user.is_verified,
        "avatar_url": user.avatar_url,
        "loyalty_bonuses": user.loyalty_bonuses,
        "spent_bonuses": user.spent_bonuses,
        "auto_apply_loyalty_points": user.auto_apply_loyalty_points,
        "unique_code": user.unique_code,
        "is_authenticated": True,
    }


@router.post("/users/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Загрузить аватар пользователя"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть изображением"
        )
    
    try:
        url = StorageService.save_avatar_image(file)
        user.avatar_url = url
        db.commit()
        db.refresh(user)
        
        logger.info("Аватар загружен", extra={"user_id": user.id, "url": url})
        return {"url": url}
    except Exception as e:
        logger.error("Ошибка загрузки аватара", extra={"user_id": user.id, "error": str(e)})
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при загрузке аватара"
        )


@router.put("/users/me")
async def update_user_profile(
    request: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Обновить профиль пользователя"""
    if request.avatar_url is not None:
        user.avatar_url = request.avatar_url
    
    db.commit()
    db.refresh(user)
    
    logger.info("Профиль обновлен", extra={"user_id": user.id})
    return {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "phone": user.phone,
        "is_verified": user.is_verified,
        "avatar_url": user.avatar_url,
        "loyalty_bonuses": user.loyalty_bonuses,
        "spent_bonuses": user.spent_bonuses,
        "auto_apply_loyalty_points": user.auto_apply_loyalty_points,
        "unique_code": user.unique_code,
    }
