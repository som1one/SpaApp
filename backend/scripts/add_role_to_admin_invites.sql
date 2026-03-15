-- Добавление колонок role и invited_by_admin_id в таблицу admin_invites

-- Проверяем и добавляем колонку role
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'admin_invites' AND column_name = 'role'
    ) THEN
        ALTER TABLE admin_invites 
        ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'admin';
        
        -- Убираем default после добавления
        ALTER TABLE admin_invites 
        ALTER COLUMN role DROP DEFAULT;
        
        RAISE NOTICE 'Колонка role добавлена';
    ELSE
        RAISE NOTICE 'Колонка role уже существует';
    END IF;
END $$;

-- Проверяем и добавляем колонку invited_by_admin_id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'admin_invites' AND column_name = 'invited_by_admin_id'
    ) THEN
        ALTER TABLE admin_invites 
        ADD COLUMN invited_by_admin_id INTEGER;
        
        RAISE NOTICE 'Колонка invited_by_admin_id добавлена';
    ELSE
        RAISE NOTICE 'Колонка invited_by_admin_id уже существует';
    END IF;
END $$;

-- Проверяем и добавляем foreign key
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_admin_invites_invited_by' 
        AND table_name = 'admin_invites'
    ) THEN
        ALTER TABLE admin_invites
        ADD CONSTRAINT fk_admin_invites_invited_by
        FOREIGN KEY (invited_by_admin_id) 
        REFERENCES admins(id) 
        ON DELETE SET NULL;
        
        RAISE NOTICE 'Foreign key fk_admin_invites_invited_by добавлен';
    ELSE
        RAISE NOTICE 'Foreign key fk_admin_invites_invited_by уже существует';
    END IF;
END $$;

