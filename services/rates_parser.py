"""
Мониторинг ставок на внешних источниках (mybuh.kz, pro1c.kz).
Вызывается планировщиком раз в месяц.
"""
import re
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import httpx

from config import settings

logger = logging.getLogger(__name__)

MONITOR_SOURCES = [
    {
        "name": "mybuh.kz",
        "url": "https://mybuh.kz/useful/stavki-nalogov-i-sotsialnykh-platezhey/",
        "patterns": {
            "mrp":      r"МРП[^\d]*(\d[\d\s]+)\s*тен",
            "mzp":      r"МЗП[^\d]*(\d[\d\s]+)\s*тен",
            "ipn":      r"ИПН[^\d]*([\d,\.]+)\s*%",
            "nds":      r"НДС[^\d]*([\d,\.]+)\s*%",
            "opv":      r"ОПВ[^\d]*([\d,\.]+)\s*%",
            "osms_emp": r"ОСМС.*?работник[а-яё]*[^\d]*([\d,\.]+)\s*%",
            "osms_er":  r"ОСМС.*?работодател[а-яё]*[^\d]*([\d,\.]+)\s*%",
            "so":       r"(?:СО|социальн\w+ отчислени\w+)[^\d]*([\d,\.]+)\s*%",
            "sn":       r"(?:СН|социальн\w+ налог)[^\d]*([\d,\.]+)\s*%",
        },
    },
    {
        "name": "pro1c.kz",
        "url": "https://pro1c.kz/buhgalteru/nalogi/",
        "patterns": {
            "mrp": r"МРП[^\d]*(\d[\d\s]+)\s*тен",
            "mzp": r"МЗП[^\d]*(\d[\d\s]+)\s*тен",
            "nds": r"НДС[^\d]*([\d,\.]+)\s*%",
        },
    },
]

# Текущие официальные значения 2026 (эталон для сравнения)
KNOWN_VALUES: dict[str, float] = {
    "mrp":      4325,
    "mzp":      85000,
    "ipn":      10.0,
    "ipn_high": 15.0,
    "nds":      16.0,
    "opv":      10.0,
    "osms_emp": 2.0,
    "osms_er":  3.0,
    "so":       3.5,
    "sn":       9.5,
    "kpn":      20.0,
    "kpn_small": 10.0,
}


def _parse_value(raw: str) -> float | None:
    cleaned = raw.replace(" ", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


async def _fetch_text(url: str) -> str:
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        resp = await client.get(url, headers={"User-Agent": "BuhKZ-RatesMonitor/1.0"})
        resp.raise_for_status()
        return resp.text


async def check_for_rate_changes() -> dict:
    """
    Обходит источники, ищет ставки по regex, сравнивает с KNOWN_VALUES.
    Возвращает {"changes": [...], "errors": [...], "sources_checked": int}.
    """
    changes: list[dict] = []
    errors: list[str] = []
    sources_checked = 0

    for source in MONITOR_SOURCES:
        try:
            text = await _fetch_text(source["url"])
            sources_checked += 1
        except Exception as exc:
            errors.append(f"{source['name']}: {exc}")
            continue

        for code, pattern in source["patterns"].items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if not match:
                continue
            found = _parse_value(match.group(1))
            if found is None:
                continue
            known = KNOWN_VALUES.get(code)
            if known is not None and abs(found - known) > 0.001:
                changes.append({
                    "source": source["name"],
                    "code": code,
                    "known_value": known,
                    "found_value": found,
                    "url": source["url"],
                })
                logger.warning(
                    "Расхождение ставки %s: ожидалось %s, найдено %s на %s",
                    code, known, found, source["name"],
                )

    return {"changes": changes, "errors": errors, "sources_checked": sources_checked}


async def send_alert_email(changes: list[dict], admin_email: str) -> None:
    if not changes:
        return

    subject = f"[BuhKZ] Обнаружены изменения ставок ({len(changes)} шт.)"
    rows = "\n".join(
        f"  • {c['code'].upper()}: ожидалось {c['known_value']}, найдено {c['found_value']} ({c['source']})"
        for c in changes
    )
    body = (
        f"Монитор BuhKZ обнаружил расхождения между известными значениями и данными на сайтах:\n\n"
        f"{rows}\n\n"
        f"Проверьте актуальность значений и при необходимости обновите ставки через\n"
        f"  python scripts/update_rates.py\n"
    )

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = settings.alert_from_email
    msg["To"] = admin_email
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            smtp.starttls()
            smtp.login(settings.smtp_user, settings.smtp_pass)
            smtp.sendmail(settings.alert_from_email, [admin_email], msg.as_string())
        logger.info("Алерт отправлен на %s", admin_email)
    except Exception as exc:
        logger.error("Не удалось отправить алерт: %s", exc)
