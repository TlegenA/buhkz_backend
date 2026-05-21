from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Date, Text, Numeric, DateTime, UniqueConstraint, Index, func, text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TaxRate(Base):
    __tablename__ = "tax_rates"
    # ADDED: rates module — составной уникальный ключ (code, valid_from)
    __table_args__ = (
        UniqueConstraint("code", "valid_from", name="uq_tax_rates_code_valid_from"),
        Index("idx_tax_rates_active", "code", postgresql_where=text("valid_to IS NULL")),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)       # ADDED: rates module
    nk_article: Mapped[str | None] = mapped_column(String(100))              # ADDED: rates module
    description: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(255))


# ADDED: rates module — история изменений ставок
class TaxRateHistory(Base):
    __tablename__ = "tax_rates_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    rate_code: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    new_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    changed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    change_notes: Mapped[str | None] = mapped_column(Text)
    detected_on: Mapped[str | None] = mapped_column(String(100))


# ADDED: rates module — лог мониторинга
class RatesMonitorLog(Base):
    __tablename__ = "rates_monitor_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    source_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str | None] = mapped_column(String(50))
    details: Mapped[str | None] = mapped_column(Text)
