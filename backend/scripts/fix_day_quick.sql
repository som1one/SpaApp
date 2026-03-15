-- Быстрое исправление через временную колонку
BEGIN;

-- Добавляем временную колонку
ALTER TABLE staff_schedules ADD COLUMN day_int INTEGER;

-- Конвертируем существующие данные
UPDATE staff_schedules SET day_int = 0 WHERE day_of_week::text = 'MONDAY';
UPDATE staff_schedules SET day_int = 1 WHERE day_of_week::text = 'TUESDAY';
UPDATE staff_schedules SET day_int = 2 WHERE day_of_week::text = 'WEDNESDAY';
UPDATE staff_schedules SET day_int = 3 WHERE day_of_week::text = 'THURSDAY';
UPDATE staff_schedules SET day_int = 4 WHERE day_of_week::text = 'FRIDAY';
UPDATE staff_schedules SET day_int = 5 WHERE day_of_week::text = 'SATURDAY';
UPDATE staff_schedules SET day_int = 6 WHERE day_of_week::text = 'SUNDAY';

-- Удаляем старую колонку
ALTER TABLE staff_schedules DROP COLUMN day_of_week CASCADE;

-- Переименовываем
ALTER TABLE staff_schedules RENAME COLUMN day_int TO day_of_week;

-- NOT NULL
ALTER TABLE staff_schedules ALTER COLUMN day_of_week SET NOT NULL;

-- Удаляем ENUM тип
DROP TYPE IF EXISTS dayofweek CASCADE;

-- Исправляем время
UPDATE staff_schedules 
SET start_time = '09:00:00', end_time = '18:00:00', 
    break_start = '13:00:00', break_end = '14:00:00'
WHERE start_time >= end_time;

COMMIT;

