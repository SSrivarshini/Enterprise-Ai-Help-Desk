"""Load company documents (text, markdown, PDF, scanned PDF, images) as LangChain Documents."""
from pathlib import Path

from langchain_core.documents import Document

from app.rag.ocr import ocr_image_file, pdf_pages

TEXT_EXT = {".txt", ".md"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def load_documents(docs_dir: Path) -> list[Document]:
    docs: list[Document] = []
    for path in sorted(Path(docs_dir).rglob("*")):
        ext = path.suffix.lower()
        if ext in TEXT_EXT:
            docs.append(Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": path.name}))
        elif ext == ".pdf":
            for number, text in enumerate(pdf_pages(path), start=1):
                if text.strip():
                    docs.append(Document(page_content=text, metadata={"source": path.name, "page": number}))
        elif ext in IMAGE_EXT:
            text = ocr_image_file(path)
            if text.strip():
                docs.append(Document(page_content=text, metadata={"source": path.name}))
    return docs
