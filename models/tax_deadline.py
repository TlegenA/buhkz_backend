from datetime import date, datetime
from sqlalchemy import String, Date, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TaxDeadline(Base):
    __tablename__ = "tax_deadlines"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    form_code: Mapped[str | None] = mapped_column(String(50))
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(50))   # ТОО, ИП, ФЛ
    tax_regime: Mapped[str | None] = mapped_column(String(100))   # Общий, УСН, СНР
    tax_type: Mapped[str | None] = mapped_column(String(100))     # ИПН, НДС, КПН
    description: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String(500))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
