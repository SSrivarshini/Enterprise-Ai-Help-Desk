import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

DOCS_DIR = ROOT / os.getenv("DOCS_DIR", "data/docs")
CHROMA_DIR = ROOT / os.getenv("CHROMA_DIR", "chroma_db")
CONTACTS_FILE = ROOT / "data" / "escalation_contacts.json"

TOP_K = int(os.getenv("TOP_K", "4"))
# Chunks scoring below this (cosine similarity) are treated as "not found" -> fallback
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.3"))

OCR_LANG = os.getenv("OCR_LANG", "eng")
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
