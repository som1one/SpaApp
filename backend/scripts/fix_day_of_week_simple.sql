-- Шаг 1: Добавляем временную колонку для хранения чисел
ALTER TABLE staff_schedules ADD COLUMN day_of_week_int INTEGER;

-- Шаг 2: Конвертируем enum значения в числа
UPDATE staff_schedules 
SET day_of_week_int = CASE day_of_week::text
    WHEN 'MONDAY' THEN 0
    WHEN 'TUESDAY' THEN 1
    WHEN 'WEDNESDAY' THEN 2
    WHEN 'THURSDAY' THEN 3
    WHEN 'FRIDAY' THEN 4
    WHEN 'SATURDAY' THEN 5
    WHEN 'SUNDAY' THEN 6
    ELSE 0
END;

-- Шаг 3: Удаляем старую колонку
ALTER TABLE staff_schedules DROP COLUMN day_of_week;

-- Шаг 4: Переименовываем новую колонку
ALTER TABLE staff_schedules RENAME COLUMN day_of_week_int TO day_of_week;

-- Шаг 5: Делаем NOT NULL
ALTER TABLE staff_schedules ALTER COLUMN day_of_week SET NOT NULL;

-- Шаг 6: Удаляем ENUM тип
DROP TYPE IF EXISTS dayofweek CASCADE;

-- Шаг 7: Исправляем некорректное время работы
UPDATE staff_schedules 
SET 
    start_time = '09:00:00',
    end_time = '18:00:00',
    break_start = '13:00:00',
    break_end = '14:00:00'
WHERE start_time >= end_time OR start_time < '06:00:00' OR end_time > '23:00:00';

