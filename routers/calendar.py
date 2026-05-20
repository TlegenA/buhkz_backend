from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from database import get_db
from models import TaxDeadline

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


class DeadlineOut(BaseModel):
    id: int
    title: str
    form_code: str | None
    due_date: date
    days_left: int
    entity_type: str | None
    tax_regime: str | None
    tax_type: str | None
    description: str | None
    source_url: str | None

    class Config:
        from_attributes = True


def _days_left(due: date) -> int:
    return (due - date.today()).days


@router.get("/", response_model=list[DeadlineOut])
async def get_deadlines(
    month: str | None = Query(None, description="Формат YYYY-MM, например 2025-06"),
    entity_type: str | None = Query(None),
    tax_regime: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    filters = []

    if month:
        year, m = map(int, month.split("-"))
        filters.append(extract("year", TaxDeadline.due_date) == year)
        filters.append(extract("month", TaxDeadline.due_date) == m)
    else:
        # По умолчанию — текущий и следующий месяц
        today = date.today()
        two_months = today + timedelta(days=62)
        filters.append(TaxDeadline.due_date >= today)
        filters.append(TaxDeadline.due_date <= two_months)

    if entity_type:
        filters.append(TaxDeadline.entity_type == entity_type)
    if tax_regime:
        filters.append(TaxDeadline.tax_regime == tax_regime)

    stmt = select(TaxDeadline).where(and_(*filters)).order_by(TaxDeadline.due_date)
    result = await db.execute(stmt)
    deadlines = result.scalars().all()

    return [
        DeadlineOut(
            id=d.id,
            title=d.title,
            form_code=d.form_code,
            due_date=d.due_date,
            days_left=_days_left(d.due_date),
            entity_type=d.entity_type,
            tax_regime=d.tax_regime,
            tax_type=d.tax_type,
            description=d.description,
            source_url=d.source_url,
        )
        for d in deadlines
    ]
