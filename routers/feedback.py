from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx

from config import settings

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    name: str = ""
    email: str = ""
    message: str = Field(..., min_length=5, max_length=2000)


@router.post("")
async def send_feedback(body: FeedbackRequest):
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        raise HTTPException(status_code=503, detail="Feedback service not configured")

    parts = ["📩 <b>Обратная связь BuhBase</b>"]
    if body.name:
        parts.append(f"👤 <b>Имя:</b> {body.name}")
    if body.email:
        parts.append(f"📧 <b>Email:</b> {body.email}")
    parts.append(f"\n💬 {body.message}")
    text = "\n".join(parts)

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
            json={"chat_id": settings.telegram_chat_id, "text": text, "parse_mode": "HTML"},
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Не удалось отправить сообщение")

    return {"ok": True}
