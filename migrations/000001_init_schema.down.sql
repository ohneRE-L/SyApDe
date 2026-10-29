-- Миграция: 000001_init_schema.down.sql
-- Откат схемы в порядке, строго обратном созданию (устранение внешних зависимостей)

DROP TABLE IF EXISTS sla_audit_logs;
DROP TABLE IF EXISTS attachments;
DROP TABLE IF EXISTS ticket_messages;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS sla_policies;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;
