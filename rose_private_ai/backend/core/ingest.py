from pathlib import Path
from bs4 import BeautifulSoup
from pypdf import PdfReader
from backend.config import settings


SUPPORTED_EXTENSIONS = {".txt", ".md", ".html", ".htm", ".pdf"}


def read_text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}. Supported: {sorted(SUPPORTED_EXTENSIONS)}")

    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")

    if suffix in {".html", ".htm"}:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(raw, "html.parser")
        return soup.get_text("\n")

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"\n[PAGE {i}]\n{text}")
        return "\n".join(pages)

    raise ValueError(f"Unsupported file type: {suffix}")


def clean_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    size = chunk_size or settings.chunk_size
    ov = overlap or settings.chunk_overlap
    if size <= ov:
        raise ValueError("CHUNK_SIZE must be greater than CHUNK_OVERLAP")

    text = clean_text(text)
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - ov, start + 1)
    return chunks


def parse_and_chunk(path: Path) -> list[str]:
    return chunk_text(read_text_from_file(path))
