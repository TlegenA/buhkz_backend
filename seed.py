"""
Начальное наполнение БД: ставки 2025/2026 и ключевые дедлайны.
Запуск: python seed.py
"""
import asyncio
from datetime import date

from sqlalchemy import select

from database import AsyncSessionLocal, create_tables
from models import TaxRate, TaxDeadline


RATES_2025 = [
    {"code": "mrp",       "name": "МРП",                 "value": 3932,  "unit": "tenge",   "valid_from": date(2025, 1, 1), "valid_to": date(2025, 12, 31), "description": "Месячный расчётный показатель 2025"},
    {"code": "mzp",       "name": "МЗП",                 "value": 85000, "unit": "tenge",   "valid_from": date(2025, 1, 1), "valid_to": date(2025, 12, 31), "description": "Минимальная заработная плата 2025"},
    {"code": "ipn",       "name": "ИПН",                 "value": 10.0,  "unit": "percent", "valid_from": date(2025, 1, 1), "valid_to": date(2025, 12, 31), "description": "Индивидуальный подоходный налог"},
    {"code": "opv",       "name": "ОПВ",                 "value": 10.0,  "unit": "percent", "valid_from": date(2025, 1, 1), "valid_to": date(2025, 12, 31), "description": "Обязательные пенсионные взносы (работник)"},
    {"code": "osms_emp",  "name": "ОСМС (сотрудник)",    "value": 2.0,   "unit": "percent", "valid_from": date(2025, 1, 1), "valid_to": date(2025, 12, 31), "description": "Обязательное медстрахование, взнос работника"},
    {"code": "osms_er",   "name": "ОСМС (работодатель)", "value": 3.0,   "unit": "percent", "valid_from": date(2025, 1, 1), "valid_to": date(2025, 12, 31), "description": "Обязательное медстрахование, взнос работодателя"},
    {"code": "so",        "name": "СО",                  "value": 3.5,   "unit": "percent", "valid_from": date(2025, 1, 1), "valid_to": date(2025, 12, 31), "description": "Социальные отчисления (работодатель)"},
    {"code": "sn",        "name": "СН",                  "value": 9.5,   "unit": "percent", "valid_from": date(2025, 1, 1), "valid_to": date(2025, 12, 31), "description": "Социальный налог (работодатель)"},
    {"code": "nds",       "name": "НДС",                 "value": 12.0,  "unit": "percent", "valid_from": date(2025, 1, 1), "valid_to": date(2025, 12, 31), "description": "Налог на добавленную стоимость"},
    {"code": "kpn",       "name": "КПН",                 "value": 20.0,  "unit": "percent", "valid_from": date(2025, 1, 1), "valid_to": date(2025, 12, 31), "description": "Корпоративный подоходный налог"},
]

RATES_2026 = [
    {"code": "mrp",        "name": "МРП",                          "value": 4325,  "unit": "tenge",   "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": None,             "source": "https://adilet.zan.kz/rus/docs/Z2500000239", "description": "Закон о бюджете № 239-VIII от 08.12.2025"},
    {"code": "mzp",        "name": "МЗП",                          "value": 85000, "unit": "tenge",   "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": None,             "source": "https://adilet.zan.kz/rus/docs/Z2500000239", "description": "Без изменений"},
    {"code": "ipn",        "name": "ИПН (до 8 500 МРП/год)",       "value": 10.0,  "unit": "percent", "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": "ст.363 НК-2026",  "source": "https://adilet.zan.kz/rus/docs/K2500000214", "description": "Базовый вычет 30 МРП (129 750 тг); 10% применяется до порога ~3,06 млн тг/мес"},
    {"code": "ipn_high",   "name": "ИПН (свыше 8 500 МРП/год)",    "value": 15.0,  "unit": "percent", "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": "ст.363 НК-2026",  "source": "https://adilet.zan.kz/rus/docs/K2500000214", "description": "Применяется к превышению порога 8 500 МРП/год (~3,06 млн тг/мес)"},
    {"code": "nds",        "name": "НДС",                          "value": 16.0,  "unit": "percent", "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": "ст.НК-2026",     "source": "https://adilet.zan.kz/rus/docs/K2500000214", "description": "Повышен с 12%; порог постановки на учёт снижен с 20 000 до 10 000 МРП (43,25 млн тг)"},
    {"code": "opv",        "name": "ОПВ (работник)",                "value": 10.0,  "unit": "percent", "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": "Соц.кодекс",     "source": "https://adilet.zan.kz", "description": None},
    {"code": "opvr",       "name": "ОПВР (работодатель)",           "value": 3.5,   "unit": "percent", "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": "Соц.кодекс",     "source": "https://adilet.zan.kz", "description": "Обязательные пенсионные взносы работодателя — новый взнос сверх оклада"},
    {"code": "osms_emp",   "name": "ВОСМС (работник)",              "value": 2.0,   "unit": "percent", "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": "Закон об ОСМС",  "source": "https://adilet.zan.kz", "description": "Потолок: 20 МЗП"},
    {"code": "osms_er",    "name": "ООСМС (работодатель)",          "value": 3.0,   "unit": "percent", "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": "Закон об ОСМС",  "source": "https://adilet.zan.kz", "description": "Потолок: 40 МЗП"},
    {"code": "so",         "name": "Социальные отчисления (СО)",    "value": 5.0,   "unit": "percent", "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": "Соц.кодекс",     "source": "https://adilet.zan.kz", "description": "5% от (gross − ОПВ), база min 1 МЗП, max 7 МЗП"},
    {"code": "sn",         "name": "Социальный налог (СН)",         "value": 6.0,   "unit": "percent", "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": "ст.НК-2026",     "source": "https://adilet.zan.kz", "description": "6% от (gross − ОПВ − ВОСМС), взаимозачёт с СО отменён"},
    {"code": "kpn",        "name": "КПН (стандарт)",                 "value": 20.0,  "unit": "percent", "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": "ст.НК-2026",     "source": "https://adilet.zan.kz/rus/docs/K2500000214", "description": None},
    {"code": "kpn_small",  "name": "КПН (малый бизнес)",             "value": 10.0,  "unit": "percent", "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": "ст.НК-2026",     "source": "https://adilet.zan.kz/rus/docs/K2500000214", "description": None},
    {"code": "vychet_base","name": "Базовый вычет ИПН",              "value": 30.0,  "unit": "mrp",     "valid_from": date(2026, 1, 1), "valid_to": None, "nk_article": "ст.НК-2026",     "source": "https://adilet.zan.kz/rus/docs/K2500000214", "description": "Повышен с 14 до 30 МРП/мес с 2026"},
]

# Дедлайны на 2025 год (квартальные и месячные)
DEADLINES_2025 = [
    # ИПН у источника выплаты (ежемесячно) — форма 200.00
    {"title": "ИПН у источника выплаты — январь",   "form_code": "200.00", "due_date": date(2025, 2, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — февраль",  "form_code": "200.00", "due_date": date(2025, 3, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — март",     "form_code": "200.00", "due_date": date(2025, 4, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — апрель",   "form_code": "200.00", "due_date": date(2025, 5, 26),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — май",      "form_code": "200.00", "due_date": date(2025, 6, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — июнь",     "form_code": "200.00", "due_date": date(2025, 7, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — июль",     "form_code": "200.00", "due_date": date(2025, 8, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — август",   "form_code": "200.00", "due_date": date(2025, 9, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — сентябрь", "form_code": "200.00", "due_date": date(2025, 10, 27), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — октябрь",  "form_code": "200.00", "due_date": date(2025, 11, 25), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — ноябрь",   "form_code": "200.00", "due_date": date(2025, 12, 25), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    # НДС (ежеквартально)
    {"title": "НДС — I квартал 2025",  "form_code": "300.00", "due_date": date(2025, 5, 15),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "НДС"},
    {"title": "НДС — II квартал 2025", "form_code": "300.00", "due_date": date(2025, 8, 15),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "НДС"},
    {"title": "НДС — III квартал 2025","form_code": "300.00", "due_date": date(2025, 11, 17), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "НДС"},
    {"title": "НДС — IV квартал 2025", "form_code": "300.00", "due_date": date(2026, 2, 16),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "НДС"},
    # КПН
    {"title": "КПН — авансовые платежи II–IV кв.", "form_code": "101.02", "due_date": date(2025, 4, 20), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "КПН"},
    {"title": "КПН — декларация за 2024 год",      "form_code": "100.00", "due_date": date(2025, 3, 31), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "КПН"},
    # ИП — упрощённая декларация
    {"title": "Упрощённая декларация ИП — I полугодие 2025",  "form_code": "910.00", "due_date": date(2025, 8, 15), "entity_type": "ИП", "tax_regime": "УСН", "tax_type": "ИПН"},
    {"title": "Упрощённая декларация ИП — II полугодие 2025", "form_code": "910.00", "due_date": date(2026, 2, 16), "entity_type": "ИП", "tax_regime": "УСН", "tax_type": "ИПН"},
    # СО / СН / ОСМС (ежемесячно, ТОО)
    {"title": "СО, СН, ОСМС за январь 2025",    "form_code": "200.00", "due_date": date(2025, 2, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за февраль 2025",   "form_code": "200.00", "due_date": date(2025, 3, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за март 2025",      "form_code": "200.00", "due_date": date(2025, 4, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за апрель 2025",    "form_code": "200.00", "due_date": date(2025, 5, 26),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за май 2025",       "form_code": "200.00", "due_date": date(2025, 6, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за июнь 2025",      "form_code": "200.00", "due_date": date(2025, 7, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
]

DEADLINES_2026 = [
    # ИПН у источника выплаты (ежемесячно) — форма 200.00
    {"title": "ИПН у источника выплаты — январь 2026",   "form_code": "200.00", "due_date": date(2026, 2, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — февраль 2026",  "form_code": "200.00", "due_date": date(2026, 3, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — март 2026",     "form_code": "200.00", "due_date": date(2026, 4, 27),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — апрель 2026",   "form_code": "200.00", "due_date": date(2026, 5, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — май 2026",      "form_code": "200.00", "due_date": date(2026, 6, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — июнь 2026",     "form_code": "200.00", "due_date": date(2026, 7, 27),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — июль 2026",     "form_code": "200.00", "due_date": date(2026, 8, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — август 2026",   "form_code": "200.00", "due_date": date(2026, 9, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — сентябрь 2026", "form_code": "200.00", "due_date": date(2026, 10, 26), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — октябрь 2026",  "form_code": "200.00", "due_date": date(2026, 11, 25), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    {"title": "ИПН у источника выплаты — ноябрь 2026",   "form_code": "200.00", "due_date": date(2026, 12, 25), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "ИПН"},
    # НДС (ежеквартально)
    {"title": "НДС — I квартал 2026",  "form_code": "300.00", "due_date": date(2026, 5, 15),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "НДС"},
    {"title": "НДС — II квартал 2026", "form_code": "300.00", "due_date": date(2026, 8, 17),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "НДС"},
    {"title": "НДС — III квартал 2026","form_code": "300.00", "due_date": date(2026, 11, 16), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "НДС"},
    {"title": "НДС — IV квартал 2026", "form_code": "300.00", "due_date": date(2027, 2, 16),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "НДС"},
    # КПН
    {"title": "КПН — авансовые платежи II–IV кв. 2026", "form_code": "101.02", "due_date": date(2026, 4, 20), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "КПН"},
    {"title": "КПН — декларация за 2025 год",           "form_code": "100.00", "due_date": date(2026, 3, 31), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "КПН"},
    # ИП — упрощённая декларация
    {"title": "Упрощённая декларация ИП — I полугодие 2026",  "form_code": "910.00", "due_date": date(2026, 8, 17), "entity_type": "ИП", "tax_regime": "УСН", "tax_type": "ИПН"},
    {"title": "Упрощённая декларация ИП — II полугодие 2026", "form_code": "910.00", "due_date": date(2027, 2, 16), "entity_type": "ИП", "tax_regime": "УСН", "tax_type": "ИПН"},
    # СО / СН / ОСМС (ежемесячно, ТОО)
    {"title": "СО, СН, ОСМС за январь 2026",    "form_code": "200.00", "due_date": date(2026, 2, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за февраль 2026",   "form_code": "200.00", "due_date": date(2026, 3, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за март 2026",      "form_code": "200.00", "due_date": date(2026, 4, 27),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за апрель 2026",    "form_code": "200.00", "due_date": date(2026, 5, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за май 2026",       "form_code": "200.00", "due_date": date(2026, 6, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за июнь 2026",      "form_code": "200.00", "due_date": date(2026, 7, 27),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за июль 2026",      "form_code": "200.00", "due_date": date(2026, 8, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за август 2026",    "form_code": "200.00", "due_date": date(2026, 9, 25),  "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за сентябрь 2026",  "form_code": "200.00", "due_date": date(2026, 10, 26), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за октябрь 2026",   "form_code": "200.00", "due_date": date(2026, 11, 25), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
    {"title": "СО, СН, ОСМС за ноябрь 2026",    "form_code": "200.00", "due_date": date(2026, 12, 25), "entity_type": "ТОО", "tax_regime": "Общий", "tax_type": "СО/СН/ОСМС"},
]


async def seed() -> None:
    await create_tables()
    async with AsyncSessionLocal() as session:
        rates_added = 0
        for data in [*RATES_2025, *RATES_2026]:
            result = await session.execute(
                select(TaxRate).where(
                    TaxRate.code == data["code"],
                    TaxRate.valid_from == data["valid_from"],
                )
            )
            if not result.scalar_one_or_none():
                session.add(TaxRate(**data))
                rates_added += 1

        deadlines_added = 0
        for data in [*DEADLINES_2025, *DEADLINES_2026]:
            result = await session.execute(
                select(TaxDeadline).where(
                    TaxDeadline.title == data["title"],
                    TaxDeadline.due_date == data["due_date"],
                )
            )
            if not result.scalar_one_or_none():
                session.add(TaxDeadline(**data))
                deadlines_added += 1

        await session.commit()
        print(f"Seed завершён: {rates_added} ставок, {deadlines_added} дедлайнов добавлено.")


if __name__ == "__main__":
    asyncio.run(seed())
