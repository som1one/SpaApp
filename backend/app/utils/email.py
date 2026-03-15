"""
Утилиты для отправки email
"""
import logging
from datetime import datetime
from typing import Optional

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


# Жёстко заданные настройки SMTP.
# ВПИШИ сюда реальные данные (особенно password), тогда почта будет работать
# даже если .env не подгрузился в контейнер.
HARDCODED_SMTP = {
    "hostname": "smtp.gmail.com",
    "port": 587,
    "username": "Priroda.eco.spa@gmail.com",
    "password": "byficbpsqcaasnjc",  # app‑password от Gmail
    "start_tls": True,
    "use_tls": False,
    "sender": "Priroda.eco.spa@gmail.com",
}


def _get_sender_email() -> str:
    """
    Получить адрес отправителя для всех email.
    Сначала берём из настроек, если нет — из HARDCODED_SMTP.
    """
    return settings.EMAIL_FROM or settings.EMAIL_USER or HARDCODED_SMTP["sender"]


def _resolve_recipient(email: str) -> tuple[str, str]:
    original = email
    if settings.EMAIL_DEBUG_RECIPIENT:
        return original, settings.EMAIL_DEBUG_RECIPIENT
    return original, email or settings.EMAIL_USER or settings.EMAIL_FROM


def _get_smtp_settings() -> dict:
    """
    Получить настройки SMTP.
    1) Берём из .env (если заданы).
    2) Если чего‑то не хватает — добиваем HARDCODED_SMTP (не падаем).
    """
    hostname = settings.EMAIL_HOST or HARDCODED_SMTP["hostname"]
    port = settings.EMAIL_PORT or HARDCODED_SMTP["port"]
    username = settings.EMAIL_USER or HARDCODED_SMTP["username"]
    password = settings.EMAIL_PASSWORD or HARDCODED_SMTP["password"]

    # Логика TLS: если порт стандартный 587/465 — настраиваем автоматически,
    # иначе берём из настроек или хардкода.
    if port == 587:
        start_tls = True
        use_tls = False
    elif port == 465:
        start_tls = False
        use_tls = True
    else:
        start_tls = settings.EMAIL_USE_TLS or HARDCODED_SMTP["start_tls"]
        use_tls = settings.EMAIL_USE_SSL or HARDCODED_SMTP["use_tls"]

    return {
        "hostname": hostname,
        "port": port,
        "username": username,
        "password": password,
        "start_tls": start_tls,
        "use_tls": use_tls,
        "sender": _get_sender_email(),
    }


async def send_booking_confirmation(
    email: str,
    service_name: str,
    appointment_datetime: datetime,
    service_price: Optional[int] = None,
    service_duration: Optional[int] = None
) -> bool:
    """
    Отправка подтверждения бронирования на email
    """
    try:
        original_email, recipient = _resolve_recipient(email)
        logger.info(
            "Отправка письма подтверждения бронирования",
            extra={
                "original_email": original_email,
                "target_email": recipient,
                "service": service_name,
                "appointment": appointment_datetime.isoformat(),
                "price": service_price,
            },
        )

        from datetime import timezone
        import pytz

        message = MIMEMultipart("alternative")
        message["Subject"] = "Подтверждение записи в SPA Salon"
        message["From"] = _get_sender_email()
        message["To"] = recipient

        moscow_tz = pytz.timezone('Europe/Moscow')
        if appointment_datetime.tzinfo is None:
            utc_datetime = appointment_datetime.replace(tzinfo=timezone.utc)
        else:
            utc_datetime = appointment_datetime.astimezone(timezone.utc)
        local_datetime = utc_datetime.astimezone(moscow_tz)
        formatted_date = local_datetime.strftime("%d.%m.%Y")
        formatted_time = local_datetime.strftime("%H:%M")

        price_text = ""
        if service_price:
            price_rubles = service_price / 100
            price_text = f"\nСтоимость: {price_rubles:.0f} ₽"

        duration_text = ""
        if service_duration:
            hours = service_duration // 60
            minutes = service_duration % 60
            if hours > 0:
                duration_text = f"\nДлительность: {hours} ч. {minutes} мин."
            else:
                duration_text = f"\nДлительность: {minutes} мин."

        text = f"""
        Здравствуйте!

        Ваша запись в SPA Salon успешно создана.

        Детали записи:
        Услуга: {service_name}
        Дата: {formatted_date}
        Время: {formatted_time}{price_text}{duration_text}

        Мы ждем вас в указанное время!

        С уважением,
        Команда SPA Salon
        """

        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #8B5A3C;">Подтверждение записи</h2>
              <p>Здравствуйте!</p>
              <p>Ваша запись в SPA Salon успешно создана.</p>
              <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Услуга:</strong> {service_name}</p>
                <p><strong>Дата:</strong> {formatted_date}</p>
                <p><strong>Время:</strong> {formatted_time}</p>
                {f'<p><strong>Стоимость:</strong> {price_rubles:.0f} ₽</p>' if service_price else ''}
                {f'<p><strong>Длительность:</strong> {duration_text.replace(chr(10), "").replace("Длительность: ", "")}</p>' if service_duration else ''}
              </div>
              <p>Мы ждем вас в указанное время!</p>
              <hr style="border: none; border-top: 1px solid #E0E0E0; margin: 30px 0;">
              <p style="color: #999; font-size: 12px;">С уважением,<br>Команда SPA Salon</p>
            </div>
          </body>
        </html>
        """

        part1 = MIMEText(text, "plain", "utf-8")
        part2 = MIMEText(html, "html", "utf-8")

        message.attach(part1)
        message.attach(part2)

        smtp_settings = _get_smtp_settings()
        await aiosmtplib.send(message, **smtp_settings)

        logger.info("Письмо подтверждения отправлено", extra={"original_email": original_email, "target_email": recipient})
        return True

    except aiosmtplib.errors.SMTPAuthenticationError as e:
        logger.error(
            "Ошибка аутентификации SMTP при отправке подтверждения бронирования",
            extra={
                "original_email": email,
                "error": str(e),
                "smtp_host": settings.EMAIL_HOST,
                "smtp_port": settings.EMAIL_PORT,
                "smtp_user": settings.EMAIL_USER,
                "hint": "Проверьте EMAIL_USER и EMAIL_PASSWORD в .env. Для Gmail используйте App Password.",
            },
            exc_info=True,
        )
        return False
    except ValueError as e:
        logger.error(
            "Ошибка конфигурации email",
            extra={"original_email": email, "error": str(e)},
            exc_info=True,
        )
        return False
    except Exception as e:
        logger.exception(
            "Ошибка отправки email подтверждения бронирования",
            extra={
                "original_email": email,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        return False


async def send_verification_code(email: str, code: str) -> bool:
    """
    Отправка кода подтверждения на email
    """
    try:
        original_email, recipient = _resolve_recipient(email)
        logger.info(
            "Отправка кода подтверждения",
            extra={"original_email": original_email, "target_email": recipient, "code": code},
        )

        message = MIMEMultipart("alternative")
        message["Subject"] = "Код подтверждения SPA Salon"
        message["From"] = _get_sender_email()
        message["To"] = recipient

        text = f"""
        Добро пожаловать в SPA Salon!

        Ваш код подтверждения: {code}

        Код действителен в течение {settings.VERIFICATION_CODE_EXPIRE_MINUTES} минут.

        Если вы не запрашивали этот код, просто проигнорируйте это письмо.
        """

        html = f"""
        <html>
          <body>
            <h2>Добро пожаловать в SPA Salon!</h2>
            <p>Ваш код подтверждения: <strong style="font-size: 24px; color: #8B5A3C;">{code}</strong></p>
            <p>Код действителен в течение {settings.VERIFICATION_CODE_EXPIRE_MINUTES} минут.</p>
            <hr>
            <p style="color: #999; font-size: 12px;">Если вы не запрашивали этот код, просто проигнорируйте это письмо.</p>
          </body>
        </html>
        """

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)

        smtp_settings = _get_smtp_settings()
        await aiosmtplib.send(message, **smtp_settings)

        logger.info("Код подтверждения отправлен", extra={"original_email": original_email, "target_email": recipient})
        return True

    except aiosmtplib.errors.SMTPAuthenticationError as e:
        logger.error(
            "Ошибка аутентификации SMTP при отправке кода подтверждения",
            extra={
                "original_email": email,
                "error": str(e),
                "smtp_host": settings.EMAIL_HOST,
                "smtp_port": settings.EMAIL_PORT,
                "smtp_user": settings.EMAIL_USER,
                "hint": "Проверьте EMAIL_USER и EMAIL_PASSWORD в .env. Для Gmail используйте App Password.",
            },
            exc_info=True,
        )
        return False
    except ValueError as e:
        logger.error(
            "Ошибка конфигурации email",
            extra={"original_email": email, "error": str(e)},
            exc_info=True,
        )
        return False
    except Exception as e:
        logger.exception(
            "Ошибка отправки кода подтверждения",
            extra={
                "original_email": email,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        return False


async def send_admin_invite_email(
    email: str,
    invite_link: str,
    role: str,
    invited_by: Optional[str] = None,
) -> bool:
    """
    Отправка приглашения администратора
    """
    try:
        original_email, recipient = _resolve_recipient(email)
        logger.info(
            "Отправка приглашения администратора",
            extra={
                "original_email": original_email,
                "target_email": recipient,
                "role": role,
                "invited_by": invited_by,
            },
        )

        message = MIMEMultipart("alternative")
        message["Subject"] = "Приглашение в админ-панель PRIRODA SPA"
        message["From"] = _get_sender_email()
        message["To"] = recipient

        role_text = "супер-администратором" if role == "super_admin" else "администратором"
        invited_by_text = f"\nВас пригласил: {invited_by}" if invited_by else ""

        text = f"""
        Здравствуйте!

        Вас пригласили стать {role_text} PRIRODA SPA.
        Перейдите по ссылке ниже, чтобы установить пароль и получить доступ:

        {invite_link}

        Ссылка действует ограниченное время.{invited_by_text}

        Если вы не ожидали это письмо, просто проигнорируйте его.
        """

        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #1E2128;">Здравствуйте!</h2>
              <p>Вас пригласили стать <strong>{'супер-администратором' if role == 'super_admin' else 'администратором'}</strong> PRIRODA SPA.</p>
              <p>Нажмите на кнопку ниже, чтобы установить пароль и войти в админ-панель.</p>
              <p style="text-align: center; margin: 30px 0;">
                <a href="{invite_link}" style="background-color: #1E2128; color: #fff; padding: 12px 24px; border-radius: 999px; text-decoration: none;">
                  Принять приглашение
                </a>
              </p>
              <p>Если кнопка не работает, скопируйте ссылку в браузер:</p>
              <p><a href="{invite_link}">{invite_link}</a></p>
              {'<p style="color: #6A6F7A;">Вас пригласил: ' + invited_by + '</p>' if invited_by else ''}
              <hr style="border: none; border-top: 1px solid #E0E0E0; margin: 30px 0;">
              <p style="color: #999; font-size: 12px;">Если вы не ожидали это письмо, просто проигнорируйте его.</p>
            </div>
          </body>
        </html>
        """

        part1 = MIMEText(text, "plain", "utf-8")
        part2 = MIMEText(html, "html", "utf-8")

        message.attach(part1)
        message.attach(part2)

        smtp_settings = _get_smtp_settings()
        logger.debug(
            f"SMTP настройки: host={smtp_settings['hostname']}, port={smtp_settings['port']}, "
            f"user={smtp_settings['username']}, start_tls={smtp_settings['start_tls']}, use_tls={smtp_settings['use_tls']}"
        )
        
        await aiosmtplib.send(message, **smtp_settings)

        logger.info(
            "Письмо приглашения отправлено",
            extra={"original_email": original_email, "target_email": recipient},
        )
        return True

    except aiosmtplib.errors.SMTPAuthenticationError as e:
        logger.error(
            "Ошибка аутентификации SMTP при отправке приглашения администратора",
            extra={
                "email": email,
                "error": str(e),
                "error_code": getattr(e, "code", None),
                "smtp_host": settings.EMAIL_HOST,
                "smtp_port": settings.EMAIL_PORT,
                "smtp_user": settings.EMAIL_USER,
                "hint": (
                    "Проверьте EMAIL_USER и EMAIL_PASSWORD в .env файле.\n"
                    "Для Gmail необходимо использовать App Password, а не обычный пароль.\n"
                    "Создайте App Password: https://myaccount.google.com/apppasswords"
                ),
            },
            exc_info=True,
        )
        return False
    except ValueError as e:
        logger.error(
            "Ошибка конфигурации email",
            extra={"email": email, "error": str(e)},
            exc_info=True,
        )
        return False
    except Exception as e:
        logger.error(
            "Ошибка отправки приглашения администратора",
            extra={
                "email": email,
                "error": str(e),
                "error_type": type(e).__name__,
                "smtp_host": settings.EMAIL_HOST,
                "smtp_port": settings.EMAIL_PORT,
            },
            exc_info=True,
        )
        return False
