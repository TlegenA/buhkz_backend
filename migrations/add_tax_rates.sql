-- migrations/add_tax_rates.sql
-- Запустить один раз на Railway:
--   psql $DATABASE_URL -f migrations/add_tax_rates.sql

-- ─── 1. Расширяем таблицу tax_rates ──────────────────────────────────────────
ALTER TABLE tax_rates ADD COLUMN IF NOT EXISTS valid_to   DATE;
ALTER TABLE tax_rates ADD COLUMN IF NOT EXISTS nk_article VARCHAR(100);

-- Убираем старый unique(code), добавляем составной (code, valid_from)
ALTER TABLE tax_rates DROP CONSTRAINT IF EXISTS tax_rates_code_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_tax_rates_code_valid_from
    ON tax_rates(code, valid_from);

-- Индекс для быстрого получения активных ставок
CREATE INDEX IF NOT EXISTS idx_tax_rates_active
    ON tax_rates(code)
    WHERE valid_to IS NULL;

-- ─── 2. Таблица истории изменений ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tax_rates_history (
    id           SERIAL PRIMARY KEY,
    rate_code    VARCHAR(50)    NOT NULL,
    old_value    NUMERIC(10, 4),
    new_value    NUMERIC(10, 4),
    changed_at   TIMESTAMP DEFAULT NOW(),
    change_notes TEXT,
    detected_on  VARCHAR(100)
);

-- ─── 3. Лог мониторинга ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS rates_monitor_log (
    id          SERIAL PRIMARY KEY,
    checked_at  TIMESTAMP DEFAULT NOW(),
    source_url  VARCHAR(500),
    status      VARCHAR(50),
    details     TEXT
);

-- ─── 4. Закрываем 2025-ставки ────────────────────────────────────────────────
UPDATE tax_rates
SET valid_to = '2025-12-31'
WHERE valid_from <= '2025-12-31'
  AND valid_to IS NULL;

-- ─── 5. Вставляем 2026-ставки ────────────────────────────────────────────────
INSERT INTO tax_rates (code, name, value, unit, valid_from, valid_to, nk_article, source, description)
VALUES
  ('mrp',        'МРП',                          4325,  'tenge',   '2026-01-01', NULL, NULL,            'https://adilet.zan.kz/rus/docs/Z2500000239', 'Закон о бюджете № 239-VIII от 08.12.2025'),
  ('mzp',        'МЗП',                          85000, 'tenge',   '2026-01-01', NULL, NULL,            'https://adilet.zan.kz/rus/docs/Z2500000239', 'Без изменений'),
  ('ipn',        'ИПН (до 1 млн тг/мес)',        10.0,  'percent', '2026-01-01', NULL, 'ст.НК-2026',   'https://adilet.zan.kz/rus/docs/K2500000214', 'Новый НК РК'),
  ('ipn_high',   'ИПН (свыше 1 млн тг/мес)',     15.0,  'percent', '2026-01-01', NULL, 'ст.НК-2026',   'https://adilet.zan.kz/rus/docs/K2500000214', 'Прогрессивная ставка с 2026'),
  ('nds',        'НДС',                          16.0,  'percent', '2026-01-01', NULL, 'ст.НК-2026',   'https://adilet.zan.kz/rus/docs/K2500000214', 'Повышен с 12%'),
  ('opv',        'ОПВ (работник)',                10.0,  'percent', '2026-01-01', NULL, 'Соц.кодекс',   'https://adilet.zan.kz', NULL),
  ('osms_emp',   'ОСМС (работник)',               2.0,   'percent', '2026-01-01', NULL, 'Закон об ОСМС','https://adilet.zan.kz', NULL),
  ('osms_er',    'ОСМС (работодатель)',            3.0,   'percent', '2026-01-01', NULL, 'Закон об ОСМС','https://adilet.zan.kz', NULL),
  ('so',         'Социальные отчисления',          3.5,   'percent', '2026-01-01', NULL, 'Соц.кодекс',   'https://adilet.zan.kz', NULL),
  ('sn',         'Социальный налог',               9.5,   'percent', '2026-01-01', NULL, 'ст.НК-2026',   'https://adilet.zan.kz', NULL),
  ('kpn',        'КПН (стандарт)',                20.0,  'percent', '2026-01-01', NULL, 'ст.НК-2026',   'https://adilet.zan.kz/rus/docs/K2500000214', NULL),
  ('kpn_small',  'КПН (малый бизнес)',            10.0,  'percent', '2026-01-01', NULL, 'ст.НК-2026',   'https://adilet.zan.kz/rus/docs/K2500000214', NULL),
  ('vychet_base','Базовый вычет ИПН',             30.0,  'mrp',     '2026-01-01', NULL, 'ст.НК-2026',   'https://adilet.zan.kz/rus/docs/K2500000214', 'Повышен с 14 до 30 МРП/мес с 2026')
ON CONFLICT (code, valid_from) DO NOTHING;
