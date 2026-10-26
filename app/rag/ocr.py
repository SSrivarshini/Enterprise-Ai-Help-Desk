"""OCR helpers: read text from image files and scanned (image-only) PDF pages."""
import io
from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

from app.config import OCR_LANG, TESSERACT_CMD

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

MIN_TEXT_CHARS = 30  # fewer characters than this on a PDF page => treat as scanned


def ocr_image(img: Image.Image) -> str:
    return pytesseract.image_to_string(img, lang=OCR_LANG)


def ocr_image_file(path: Path) -> str:
    with Image.open(path) as img:
        return ocr_image(img)


def pdf_pages(path: Path) -> list[str]:
    """Return the text of each page. Digital pages use the embedded text layer,
    scanned pages are rendered to an image and run through OCR."""
    pages = []
    with fitz.open(path) as doc:
        for page in doc:
            text = page.get_text().strip()
            if len(text) < MIN_TEXT_CHARS:
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text = ocr_image(img).strip()
            pages.append(text)
    return pages
