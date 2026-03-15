"""Исправление типа day_of_week и данных расписания"""
from sqlalchemy import create_engine, text
from datetime import time
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.staff import StaffSchedule

def main():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("Шаг 1: Конвертируем ENUM значения в числа...")
        
        # Маппинг enum -> integer
        day_mapping = {
            'MONDAY': 0,
            'TUESDAY': 1,
            'WEDNESDAY': 2,
            'THURSDAY': 3,
            'FRIDAY': 4,
            'SATURDAY': 5,
            'SUNDAY': 6,
        }
        
        # Получаем текущие данные
        result = conn.execute(text("SELECT id, day_of_week FROM staff_schedules"))
        schedules_data = result.fetchall()
        
        print(f"Найдено {len(schedules_data)} расписаний для конвертации")
        
        # Конвертируем каждую строку
        for schedule_id, day_enum in schedules_data:
            day_int = day_mapping.get(day_enum, 0)
            print(f"  ID {schedule_id}: {day_enum} -> {day_int}")
        
        print("\nШаг 2: Удаляем ENUM тип и создаем INTEGER колонку...")
        
        # Удаляем старую колонку
        conn.execute(text("ALTER TABLE staff_schedules DROP COLUMN day_of_week"))
        
        # Создаем новую колонку как INTEGER
        conn.execute(text("ALTER TABLE staff_schedules ADD COLUMN day_of_week INTEGER NOT NULL DEFAULT 0"))
        
        # Обновляем значения
        for schedule_id, day_enum in schedules_data:
            day_int = day_mapping.get(day_enum, 0)
            conn.execute(
                text(f"UPDATE staff_schedules SET day_of_week = {day_int} WHERE id = {schedule_id}")
            )
        
        # Удаляем старый enum тип
        conn.execute(text("DROP TYPE IF EXISTS dayofweek CASCADE"))
        
        conn.commit()
        print("\n✅ Тип day_of_week изменен на INTEGER")
    
    # Исправляем некорректные данные времени
    print("\nШаг 3: Исправляю некорректное время работы...")
    db = SessionLocal()
    
    schedules = db.query(StaffSchedule).all()
    for schedule in schedules:
        print(f"\n  Schedule ID {schedule.id}, Day {schedule.day_of_week}:")
        print(f"    Было: {schedule.start_time} - {schedule.end_time}")
        
        # Проверяем корректность времени
        if schedule.start_time >= schedule.end_time:
            print(f"    ⚠️ Некорректное время! Исправляю на 09:00 - 18:00")
            schedule.start_time = time(9, 0)
            schedule.end_time = time(18, 0)
            schedule.break_start = time(13, 0)
            schedule.break_end = time(14, 0)
        else:
            print(f"    ✓ Время корректно")
    
    db.commit()
    db.close()
    
    print("\n✅ Все данные исправлены!")

if __name__ == "__main__":
    main()

