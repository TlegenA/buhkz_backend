from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

from database import get_db
from models import TaxRate

router = APIRouter(prefix="/api/rates", tags=["rates"])


class TaxRateOut(BaseModel):
    id: int
    code: str
    name: str
    value: Decimal
    unit: str
    valid_from: date
    valid_to: date | None       # ADDED: rates module
    nk_article: str | None      # ADDED: rates module
    description: str | None

    class Config:
        from_attributes = True


# ADDED: rates module — быстрые эндпоинты для МРП/МЗП (до /{code})
@router.get("/mrp")
async def get_mrp(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TaxRate).where(TaxRate.code == "mrp", TaxRate.valid_to == None)
    )
    rate = result.scalar_one_or_none()
    if not rate:
        return {"value": 4325, "valid_from": "2026-01-01", "source": "fallback"}
    return {"value": float(rate.value), "valid_from": rate.valid_from.isoformat(), "source": rate.source}


@router.get("/mzp")
async def get_mzp(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TaxRate).where(TaxRate.code == "mzp", TaxRate.valid_to == None)
    )
    rate = result.scalar_one_or_none()
    if not rate:
        return {"value": 85000, "valid_from": "2026-01-01", "source": "fallback"}
    return {"value": float(rate.value), "valid_from": rate.valid_from.isoformat(), "source": rate.source}


@router.get("/", response_model=list[TaxRateOut])
async def get_all_rates(db: AsyncSession = Depends(get_db)):
    # ADDED: rates module — только актуальные ставки (valid_to IS NULL)
    result = await db.execute(
        select(TaxRate).where(TaxRate.valid_to == None).order_by(TaxRate.code)
    )
    return result.scalars().all()


# ADDED: rates module — история конкретной ставки (до /{code})
@router.get("/history/{code}", response_model=list[TaxRateOut])
async def get_rate_history(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TaxRate).where(TaxRate.code == code).order_by(TaxRate.valid_from.desc())
    )
    rows = result.scalars().all()
    if not rows:
        raise HTTPException(status_code=404, detail=f"Ставка '{code}' не найдена")
    return rows


@router.get("/{code}", response_model=TaxRateOut)
async def get_rate(code: str, db: AsyncSession = Depends(get_db)):
    # ADDED: rates module — возвращаем активную ставку (valid_to IS NULL)
    result = await db.execute(
        select(TaxRate).where(TaxRate.code == code, TaxRate.valid_to == None)
    )
    rate = result.scalar_one_or_none()
    if not rate:
        raise HTTPException(status_code=404, detail=f"Ставка '{code}' не найдена")
    return rate
