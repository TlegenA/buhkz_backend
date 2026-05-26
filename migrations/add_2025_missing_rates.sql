-- migrations/add_2025_missing_rates.sql
-- Добавляет недостающие ставки 2025 года для корректного отображения истории.
-- Запустить один раз:
--   psql $DATABASE_URL -f migrations/add_2025_missing_rates.sql

-- ОПВР (работодатель) — 2.5% в 2025 (повышен до 3.5% с 2026)
INSERT INTO tax_rates (code, name, value, unit, valid_from, valid_to, description)
VALUES (
    'opvr',
    'ОПВР (работодатель)',
    2.5,
    'percent',
    '2025-01-01',
    '2025-12-31',
    'Обязательные пенсионные взносы работодателя (повышен до 3.5% с 2026)'
)
ON CONFLICT (code, valid_from) DO NOTHING;

-- Базовый вычет ИПН — 14 МРП/мес в 2025 (повышен до 30 МРП с 2026)
INSERT INTO tax_rates (code, name, value, unit, valid_from, valid_to, description)
VALUES (
    'vychet_base',
    'Базовый вычет ИПН',
    14.0,
    'mrp',
    '2025-01-01',
    '2025-12-31',
    'Повышен с 14 до 30 МРП/мес с 2026'
)
ON CONFLICT (code, valid_from) DO NOTHING;
