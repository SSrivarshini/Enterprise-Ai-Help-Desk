import logging
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from app.config import TELEGRAM_WEBHOOK_SECRET
from app.rag.chain import HelpDesk
from app.telegram_client import send_message

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("helpdesk")

WELCOME = (
    "Hi! I'm the Enterprise Help Desk assistant. Ask me about HR policies, onboarding, "
    "leave, payroll, IT procedures and other internal processes."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.desk = HelpDesk()
    yield


app = FastAPI(title="Enterprise AI Help Desk", lifespan=lifespan)


class Question(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(body: Question, request: Request):
    """Ask a question over HTTP (useful for testing without Telegram)."""
    return request.app.state.desk.ask(body.question)


def reply(desk: HelpDesk, chat_id: int, text: str) -> None:
    try:
        result = desk.ask(text)
        message = result["answer"]
        if result["sources"]:
            message += "\n\nSources: " + ", ".join(result["sources"])
    except Exception:
        log.exception("Help desk failed")
        message = "Sorry, something went wrong. Please try again in a moment."
    send_message(chat_id, message)


@app.post("/webhook")
async def webhook(
    request: Request,
    background: BackgroundTasks,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if TELEGRAM_WEBHOOK_SECRET and x_telegram_bot_api_secret_token != TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret token")

    update = await request.json()
    message = update.get("message") or {}
    text, chat = message.get("text"), message.get("chat", {})
    if not text or "id" not in chat:
        return {"ok": True}

    if text.startswith("/start"):
        background.add_task(send_message, chat["id"], WELCOME)
    else:
        background.add_task(reply, request.app.state.desk, chat["id"], text)
    return {"ok": True}
