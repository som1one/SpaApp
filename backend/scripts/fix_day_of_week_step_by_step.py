"""Пошаговое исправление типа day_of_week с детальным логированием"""
from sqlalchemy import create_engine, text
import time
from app.core.config import settings

def execute_and_log(conn, sql, description):
    """Выполняет SQL с логированием"""
    print(f"\n{'='*60}")
    print(f"⏳ {description}")
    print(f"SQL: {sql[:100]}...")
    start = time.time()
    
    try:
        result = conn.execute(text(sql))
        elapsed = time.time() - start
        print(f"✅ Выполнено за {elapsed:.2f}с")
        return result
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Ошибка после {elapsed:.2f}с: {e}")
        raise

def main():
    print("🚀 Начало исправления day_of_week...")
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
    
    with engine.begin() as conn:
        # Шаг 1: Получаем текущие данные
        result = execute_and_log(
            conn,
            "SELECT id, day_of_week, start_time, end_time FROM staff_schedules",
            "Получение текущих данных"
        )
        schedules_data = [(row[0], row[1], row[2], row[3]) for row in result.fetchall()]
        print(f"\n📊 Найдено {len(schedules_data)} расписаний:")
        for sid, day_enum, start, end in schedules_data:
            print(f"   ID {sid}: {day_enum}, {start} - {end}")
        
        # Шаг 2: Добавляем временную колонку
        execute_and_log(
            conn,
            "ALTER TABLE staff_schedules ADD COLUMN IF NOT EXISTS day_of_week_int INTEGER DEFAULT 0",
            "Добавление временной колонки day_of_week_int"
        )
        
        # Шаг 3: Конвертируем значения по одной записи
        print(f"\n⏳ Конвертация значений...")
        for schedule_id, day_enum, _, _ in schedules_data:
            day_int = day_mapping.get(day_enum, 0)
            conn.execute(
                text("UPDATE staff_schedules SET day_of_week_int = :day_int WHERE id = :id"),
                {"day_int": day_int, "id": schedule_id}
            )
            print(f"   ✓ ID {schedule_id}: {day_enum} -> {day_int}")
        
        # Шаг 4: Удаляем старую колонку
        execute_and_log(
            conn,
            "ALTER TABLE staff_schedules DROP COLUMN day_of_week CASCADE",
            "Удаление старой колонки day_of_week"
        )
        
        # Шаг 5: Переименовываем
        execute_and_log(
            conn,
            "ALTER TABLE staff_schedules RENAME COLUMN day_of_week_int TO day_of_week",
            "Переименование day_of_week_int -> day_of_week"
        )
        
        # Шаг 6: NOT NULL
        execute_and_log(
            conn,
            "ALTER TABLE staff_schedules ALTER COLUMN day_of_week SET NOT NULL",
            "Установка NOT NULL для day_of_week"
        )
        
        # Шаг 7: Удаляем ENUM тип
        try:
            execute_and_log(
                conn,
                "DROP TYPE IF EXISTS dayofweek CASCADE",
                "Удаление ENUM типа dayofweek"
            )
        except Exception as e:
            print(f"⚠️ Предупреждение при удалении типа (можно игнорировать): {e}")
        
        # Шаг 8: Исправляем некорректное время
        execute_and_log(
            conn,
            """UPDATE staff_schedules 
               SET start_time = '09:00:00', end_time = '18:00:00', 
                   break_start = '13:00:00', break_end = '14:00:00'
               WHERE start_time >= end_time""",
            "Исправление некорректного времени работы"
        )
        
        print(f"\n{'='*60}")
        print("🎉 Все изменения применены!")
    
    # Проверка результата
    with engine.connect() as conn:
        print(f"\n{'='*60}")
        print("📋 Проверка результата:")
        result = conn.execute(text("SELECT id, staff_id, day_of_week, start_time, end_time FROM staff_schedules"))
        for row in result.fetchall():
            print(f"   ID: {row[0]}, Staff: {row[1]}, Day: {row[2]} ({type(row[2]).__name__}), {row[3]} - {row[4]}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

