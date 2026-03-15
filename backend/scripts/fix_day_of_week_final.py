"""Исправление типа day_of_week через Python"""
from sqlalchemy import create_engine, text
from datetime import time
from app.core.config import settings

def main():
    engine = create_engine(settings.DATABASE_URL)
    
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
    
    with engine.begin() as conn:  # Используем транзакцию
        print("Шаг 1: Получаем текущие данные...")
        result = conn.execute(text("SELECT id, day_of_week FROM staff_schedules"))
        schedules_data = [(row[0], row[1]) for row in result.fetchall()]
        print(f"Найдено {len(schedules_data)} расписаний")
        
        for schedule_id, day_enum in schedules_data:
            day_int = day_mapping.get(day_enum, 0)
            print(f"  ID {schedule_id}: {day_enum} -> {day_int}")
        
        print("\nШаг 2: Добавляем временную колонку...")
        conn.execute(text("ALTER TABLE staff_schedules ADD COLUMN IF NOT EXISTS day_of_week_int INTEGER"))
        
        print("\nШаг 3: Конвертируем значения...")
        for schedule_id, day_enum in schedules_data:
            day_int = day_mapping.get(day_enum, 0)
            conn.execute(
                text("UPDATE staff_schedules SET day_of_week_int = :day_int WHERE id = :id"),
                {"day_int": day_int, "id": schedule_id}
            )
        
        print("\nШаг 4: Удаляем старую колонку...")
        conn.execute(text("ALTER TABLE staff_schedules DROP COLUMN day_of_week CASCADE"))
        
        print("\nШаг 5: Переименовываем новую колонку...")
        conn.execute(text("ALTER TABLE staff_schedules RENAME COLUMN day_of_week_int TO day_of_week"))
        
        print("\nШаг 6: Устанавливаем NOT NULL...")
        conn.execute(text("ALTER TABLE staff_schedules ALTER COLUMN day_of_week SET NOT NULL"))
        
        print("\nШаг 7: Удаляем ENUM тип...")
        try:
            conn.execute(text("DROP TYPE IF EXISTS dayofweek CASCADE"))
        except Exception as e:
            print(f"Предупреждение при удалении типа: {e}")
        
        print("\nШаг 8: Исправляем некорректное время...")
        conn.execute(text("""
            UPDATE staff_schedules 
            SET 
                start_time = '09:00:00',
                end_time = '18:00:00',
                break_start = '13:00:00',
                break_end = '14:00:00'
            WHERE start_time >= end_time
        """))
        
        print("\n✅ Все изменения применены!")
    
    # Проверяем результат
    with engine.connect() as conn:
        print("\nПроверка результата:")
        result = conn.execute(text("SELECT id, staff_id, day_of_week, start_time, end_time FROM staff_schedules"))
        for row in result.fetchall():
            print(f"  ID: {row[0]}, Staff: {row[1]}, Day: {row[2]} (type: {type(row[2])}), {row[3]} - {row[4]}")

if __name__ == "__main__":
    main()

