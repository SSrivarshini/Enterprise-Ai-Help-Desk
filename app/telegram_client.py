import httpx

from app.config import TELEGRAM_BOT_TOKEN


def send_message(chat_id: int, text: str) -> None:
    httpx.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=15,
    )
