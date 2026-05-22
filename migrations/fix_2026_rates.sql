-- migrations/fix_2026_rates.sql
-- Исправляет ошибочные значения ставок 2026 года в таблице tax_rates.
-- Запустить один раз:
--   psql $DATABASE_URL -f migrations/fix_2026_rates.sql

-- СО: 3.5% → 5% (Социальный кодекс РК, с 2026)
UPDATE tax_rates
SET value = 5.0,
    name = 'Социальные отчисления (СО)',
    description = '5% от (gross − ОПВ), база min 1 МЗП, max 7 МЗП'
WHERE code = 'so' AND valid_from = '2026-01-01';

-- СН: 9.5% → 6% (НК РК 2026, взаимозачёт с СО отменён)
UPDATE tax_rates
SET value = 6.0,
    name = 'Социальный налог (СН)',
    description = '6% от (gross − ОПВ − ВОСМС), взаимозачёт с СО отменён',
    nk_article = 'ст.НК-2026'
WHERE code = 'sn' AND valid_from = '2026-01-01';

-- ИПН: уточнить описание порога (не 1 млн/мес, а 8 500 МРП/год)
UPDATE tax_rates
SET name = 'ИПН (до 8 500 МРП/год)',
    description = 'Базовый вычет 30 МРП (129 750 тг); 10% применяется до порога ~3,06 млн тг/мес',
    nk_article = 'ст.363 НК-2026'
WHERE code = 'ipn' AND valid_from = '2026-01-01';

UPDATE tax_rates
SET name = 'ИПН (свыше 8 500 МРП/год)',
    description = 'Применяется к превышению порога 8 500 МРП/год (~3,06 млн тг/мес)',
    nk_article = 'ст.363 НК-2026'
WHERE code = 'ipn_high' AND valid_from = '2026-01-01';

-- ВОСМС/ООСМС: уточнить названия
UPDATE tax_rates
SET name = 'ВОСМС (работник)',
    description = 'Потолок: 20 МЗП'
WHERE code = 'osms_emp' AND valid_from = '2026-01-01';

UPDATE tax_rates
SET name = 'ООСМС (работодатель)',
    description = 'Потолок: 40 МЗП'
WHERE code = 'osms_er' AND valid_from = '2026-01-01';

-- ОПВР (работодатель) — новый взнос с 2026 года
INSERT INTO tax_rates (code, name, value, unit, valid_from, valid_to, nk_article, source, description)
VALUES (
    'opvr',
    'ОПВР (работодатель)',
    3.5,
    'percent',
    '2026-01-01',
    NULL,
    'Соц.кодекс',
    'https://adilet.zan.kz',
    'Обязательные пенсионные взносы работодателя — новый взнос сверх оклада'
)
ON CONFLICT (code, valid_from) DO UPDATE
    SET value = EXCLUDED.value,
        description = EXCLUDED.description;
