from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.services.loyalty_service import award_loyalty_for_booking


client = TestClient(app)


def test_award_loyalty_for_completed_booking_only_once():
  db = SessionLocal()
  user_id = None
  booking_id = None

  old_enabled = settings.LOYALTY_ENABLED
  old_rate = settings.LOYALTY_POINTS_PER_100_RUB

  try:
    # Включаем программу лояльности и задаём предсказуемый коэффициент
    settings.LOYALTY_ENABLED = True
    settings.LOYALTY_POINTS_PER_100_RUB = 5  # 5 баллов за каждые 100 ₽

    # Создаём тестового пользователя
    user = User(
      name="[TEST] Loyalty",
      surname="User",
      email="loyalty_test@example.com",
      hashed_password="test",
      phone="79990000000",
      is_verified=True,
      is_active=True,
      loyalty_points=0,  # Используем loyalty_points вместо loyalty_level
    )
    db.add(user)
    db.flush()
    user_id = user.id

    # Создаём завершённую запись со стоимостью 1000 ₽ (100000 копеек)
    booking = Booking(
      user_id=user.id,
      service_name="[TEST] Услуга",
      service_duration=60,
      service_price=100000,  # 1000 ₽ в копейках
      appointment_datetime="2025-01-01T10:00:00+03:00",
      status=BookingStatus.COMPLETED,
      phone="79990000000",
      notes="[TEST] YClients. ID: 999999",
    )
    db.add(booking)
    db.flush()
    booking_id = booking.id

    # Первое начисление
    # При 0 баллах пользователь на 1 уровне (Бронза) с 3% кэшбэком
    # 1000 ₽ * 3% = 30 баллов
    award_loyalty_for_booking(db, user, booking)
    db.commit()
    db.refresh(user)
    db.refresh(booking)

    # 1000 ₽ * 3% = 30 баллов (1 уровень, Бронза)
    assert user.loyalty_points == 30
    assert booking.loyalty_points_awarded is True
    assert booking.loyalty_points_amount == 30

    # Повторный вызов не должен менять баланс
    previous_points = user.loyalty_points
    award_loyalty_for_booking(db, user, booking)
    db.commit()
    db.refresh(user)

    assert user.loyalty_points == previous_points

  finally:
    # Очищаем тестовые данные и возвращаем настройки
    if booking_id is not None:
      db.query(Booking).filter(Booking.id == booking_id).delete(synchronize_session=False)
    if user_id is not None:
      db.query(User).filter(User.id == user_id).delete(synchronize_session=False)
    db.commit()
    db.close()

    settings.LOYALTY_ENABLED = old_enabled
    settings.LOYALTY_POINTS_PER_100_RUB = old_rate


