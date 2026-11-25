-- Миграция: 000002_seed_sla_policies.up.sql
-- Начальное заполнение регламентов SLA для всех уровней приоритета

INSERT INTO sla_policies (priority, max_first_response_time_minutes, max_resolution_time_minutes)
VALUES
    ('LOW',      480,  2880),
    ('MEDIUM',   240,  1440),
    ('HIGH',      60,   480),
    ('CRITICAL',  15,   120)
ON CONFLICT (priority) DO NOTHING;
