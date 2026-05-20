import httpx
from bs4 import BeautifulSoup

KGD_CALENDAR_URL = "https://kgd.gov.kz/ru/section/kalendar-nalogoplatelshchika"


async def fetch_kgd_calendar() -> str:
    """Загружает страницу налогового календаря КГД."""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(KGD_CALENDAR_URL, follow_redirects=True)
        response.raise_for_status()
        return response.text


async def parse_kgd_deadlines(html: str) -> list[dict]:
    """Извлекает дедлайны из HTML страницы КГД (заглушка — структура сайта меняется)."""
    soup = BeautifulSoup(html, "lxml")
    deadlines = []

    # КГД публикует календарь в виде таблиц — парсим все таблицы на странице
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        for row in rows[1:]:  # пропускаем заголовок
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 3:
                deadlines.append({
                    "raw_date": cols[0],
                    "title": cols[1] if len(cols) > 1 else "",
                    "form_code": cols[2] if len(cols) > 2 else "",
                })

    return deadlines
