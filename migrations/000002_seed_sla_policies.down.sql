-- Миграция: 000002_seed_sla_policies.down.sql
DELETE FROM sla_policies WHERE priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
