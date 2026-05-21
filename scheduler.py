import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from services.parser import fetch_kgd_calendar, parse_kgd_deadlines
from services.rates_parser import check_for_rate_changes, send_alert_email, MONITOR_SOURCES
from config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Almaty")


@scheduler.scheduled_job("cron", day=1, hour=9, minute=0)
async def check_kgd_updates():
    """Раз в месяц проверяет налоговый календарь КГД на изменения."""
    try:
        html = await fetch_kgd_calendar()
        deadlines = await parse_kgd_deadlines(html)
        logger.info("КГД: получено %d записей из календаря", len(deadlines))
        # TODO: сравнить с БД и отправить алерт при изменениях
    except Exception as exc:
        logger.error("Ошибка при проверке КГД: %s", exc)


@scheduler.scheduled_job("cron", day=1, hour=10, minute=0)
async def check_rates_updates():
    """Раз в месяц мониторит внешние источники на изменение ставок."""
    from database import AsyncSessionLocal
    from models import RatesMonitorLog

    result = await check_for_rate_changes()

    status = "changes_found" if result["changes"] else "ok"
    if result["errors"]:
        status = "error" if not result["sources_checked"] else status

    details_parts = []
    if result["changes"]:
        details_parts.append(
            "Расхождения: " + "; ".join(
                f"{c['code']}={c['found_value']} (ожидалось {c['known_value']}) на {c['source']}"
                for c in result["changes"]
            )
        )
    if result["errors"]:
        details_parts.append("Ошибки: " + "; ".join(result["errors"]))

    async with AsyncSessionLocal() as session:
        session.add(RatesMonitorLog(
            source_url=", ".join(s["url"] for s in MONITOR_SOURCES),
            status=status,
            details="\n".join(details_parts) or None,
        ))
        await session.commit()

    if result["changes"] and settings.admin_email:
        await send_alert_email(result["changes"], settings.admin_email)
        logger.info("Алерт по ставкам отправлен: %d расхождений", len(result["changes"]))
    elif result["changes"]:
        logger.warning(
            "Обнаружены расхождения ставок, но ADMIN_EMAIL не задан: %s",
            result["changes"],
        )
    else:
        logger.info("Мониторинг ставок: расхождений не найдено (%d источников)", result["sources_checked"])
