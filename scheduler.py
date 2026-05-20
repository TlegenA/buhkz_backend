import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.parser import fetch_kgd_calendar, parse_kgd_deadlines

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
