"""
Утилиты для работы с московским временем
"""
import pytz
from datetime import datetime
from typing import Optional

# Московский часовой пояс
MOSCOW_TZ = pytz.timezone('Europe/Moscow')


def moscow_now() -> datetime:
    """Возвращает текущее время в московском часовом поясе"""
    return datetime.now(MOSCOW_TZ)


def to_moscow(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Конвертирует datetime в московское время.
    Если datetime naive (без timezone), предполагает что это уже московское время.
    Если datetime aware (с timezone), конвертирует в московское.
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # Если время без timezone, предполагаем что это московское
        return MOSCOW_TZ.localize(dt)
    
    # Конвертируем в московское время
    return dt.astimezone(MOSCOW_TZ)


def moscow_datetime(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0) -> datetime:
    """Создает datetime в московском часовом поясе"""
    dt = datetime(year, month, day, hour, minute, second)
    return MOSCOW_TZ.localize(dt)

