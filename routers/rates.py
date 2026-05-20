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
    description: str | None

    class Config:
        from_attributes = True


@router.get("/", response_model=list[TaxRateOut])
async def get_all_rates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TaxRate).order_by(TaxRate.code))
    return result.scalars().all()


@router.get("/{code}", response_model=TaxRateOut)
async def get_rate(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TaxRate).where(TaxRate.code == code))
    rate = result.scalar_one_or_none()
    if not rate:
        raise HTTPException(status_code=404, detail=f"Ставка '{code}' не найдена")
    return rate
