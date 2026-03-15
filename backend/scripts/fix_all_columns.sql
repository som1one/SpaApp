-- Исправление колонок в таблице users
-- Переименование loyalty_points в loyalty_bonuses (если существует)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'loyalty_points'
    ) THEN
        ALTER TABLE users RENAME COLUMN loyalty_points TO loyalty_bonuses;
        RAISE NOTICE 'Переименовано loyalty_points -> loyalty_bonuses';
    END IF;
END $$;

-- Добавление spent_bonuses (если не существует)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'spent_bonuses'
    ) THEN
        ALTER TABLE users ADD COLUMN spent_bonuses INTEGER NOT NULL DEFAULT 0;
        RAISE NOTICE 'Добавлено spent_bonuses';
    END IF;
END $$;

-- Исправление колонок в таблице bookings
-- Переименование loyalty_points_awarded в loyalty_bonuses_awarded (если существует)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'bookings' AND column_name = 'loyalty_points_awarded'
    ) THEN
        ALTER TABLE bookings RENAME COLUMN loyalty_points_awarded TO loyalty_bonuses_awarded;
        RAISE NOTICE 'Переименовано loyalty_points_awarded -> loyalty_bonuses_awarded';
    END IF;
END $$;

-- Переименование loyalty_points_amount в loyalty_bonuses_amount (если существует)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'bookings' AND column_name = 'loyalty_points_amount'
    ) THEN
        ALTER TABLE bookings RENAME COLUMN loyalty_points_amount TO loyalty_bonuses_amount;
        RAISE NOTICE 'Переименовано loyalty_points_amount -> loyalty_bonuses_amount';
    END IF;
END $$;

-- Исправление колонок в таблице loyalty_levels
-- Переименование min_points в min_bonuses (если существует)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'loyalty_levels' AND column_name = 'min_points'
    ) THEN
        ALTER TABLE loyalty_levels RENAME COLUMN min_points TO min_bonuses;
        RAISE NOTICE 'Переименовано min_points -> min_bonuses';
    END IF;
END $$;

