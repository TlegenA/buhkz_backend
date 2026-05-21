"""
Интерактивный CLI для ручного обновления налоговых ставок.
Запуск: python scripts/update_rates.py
"""
import asyncio
import sys
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Добавляем backend/ в путь, чтобы импорты работали из любого места
sys.path.insert(0, __file__.rsplit("/scripts/", 1)[0].rsplit("\\scripts\\", 1)[0])

from database import AsyncSessionLocal, create_tables
from models import TaxRate, TaxRateHistory


RATE_LABELS = {
    "mrp":        "МРП (тенге)",
    "mzp":        "МЗП (тенге)",
    "ipn":        "ИПН до 1 млн/мес (%)",
    "ipn_high":   "ИПН свыше 1 млн/мес (%)",
    "nds":        "НДС (%)",
    "opv":        "ОПВ работник (%)",
    "osms_emp":   "ОСМС работник (%)",
    "osms_er":    "ОСМС работодатель (%)",
    "so":         "СО (%)",
    "sn":         "СН (%)",
    "kpn":        "КПН стандарт (%)",
    "kpn_small":  "КПН малый бизнес (%)",
    "vychet_base":"Базовый вычет ИПН (МРП/мес)",
}


def _prompt(label: str, current: Decimal) -> Decimal | None:
    raw = input(f"  {label} [{current}]: ").strip()
    if not raw:
        return None
    try:
        return Decimal(raw)
    except Exception:
        print(f"  Некорректное значение '{raw}', пропускаем.")
        return None


async def run(year: int) -> None:
    await create_tables()
    valid_from = date(year, 1, 1)
    notes = input(f"Примечание к обновлению {year} (Enter — пропустить): ").strip() or None

    async with AsyncSessionLocal() as session:
        # Загружаем все активные ставки (valid_to IS NULL)
        result = await session.execute(
            select(TaxRate).where(TaxRate.valid_to == None)
        )
        active: dict[str, TaxRate] = {r.code: r for r in result.scalars().all()}

        changes: list[tuple[TaxRate, Decimal]] = []

        print(f"\nВведите новые значения для ставок {year}. Enter = оставить без изменений.\n")
        for code, label in RATE_LABELS.items():
            current_rate = active.get(code)
            if current_rate is None:
                print(f"  {label} — ставка '{code}' не найдена в БД, пропускаем.")
                continue
            new_val = _prompt(label, current_rate.value)
            if new_val is not None and new_val != current_rate.value:
                changes.append((current_rate, new_val))

        if not changes:
            print("\nИзменений нет, выход.")
            return

        print(f"\nБудут обновлены {len(changes)} ставок:")
        for rate, new_val in changes:
            print(f"  {rate.code}: {rate.value} → {new_val}")

        confirm = input("\nПодтвердить? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Отменено.")
            return

        for rate, new_val in changes:
            # Закрываем текущую запись
            rate.valid_to = date(year - 1, 12, 31)

            # Создаём новую запись
            new_rate = TaxRate(
                code=rate.code,
                name=rate.name,
                value=new_val,
                unit=rate.unit,
                valid_from=valid_from,
                valid_to=None,
                nk_article=rate.nk_article,
                description=rate.description,
                source=rate.source,
            )
            session.add(new_rate)

            # Пишем в историю
            session.add(TaxRateHistory(
                rate_code=rate.code,
                old_value=rate.value,
                new_value=new_val,
                change_notes=notes,
                detected_on="manual-cli",
            ))

        await session.commit()
        print(f"\nГотово: обновлено {len(changes)} ставок на {year} год.")


if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else date.today().year
    asyncio.run(run(year))
