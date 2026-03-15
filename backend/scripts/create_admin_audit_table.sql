-- Создание таблицы admin_audit, если её нет
CREATE TABLE IF NOT EXISTS admin_audit (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    admin_id INTEGER NOT NULL,
    action VARCHAR(255) NOT NULL,
    entity VARCHAR(100),
    entity_id INTEGER,
    payload JSONB,
    user_agent TEXT,
    ip_address VARCHAR(45),
    executed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE
);

-- Создание индексов для быстрого поиска
CREATE INDEX IF NOT EXISTS ix_admin_audit_admin_id ON admin_audit(admin_id);
CREATE INDEX IF NOT EXISTS ix_admin_audit_action ON admin_audit(action);
CREATE INDEX IF NOT EXISTS ix_admin_audit_entity ON admin_audit(entity);
CREATE INDEX IF NOT EXISTS ix_admin_audit_executed_at ON admin_audit(executed_at);

