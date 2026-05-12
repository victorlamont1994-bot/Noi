from __future__ import annotations

from pathlib import Path
from collections import Counter
import json
import math
import re

from backend.config import settings
from backend.core.ingest import parse_and_chunk
from backend.core.audit import sha256_text


TOKEN_RE = re.compile(r"[a-zA-Z0-9_\-]{2,}")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def append_chunk(record: dict) -> None:
    path = Path(settings.index_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def read_chunks() -> list[dict]:
    path = Path(settings.index_path)
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def ingest_file(path: Path) -> dict:
    chunks = parse_and_chunk(path)
    for i, chunk in enumerate(chunks):
        append_chunk({
            "id": sha256_text(f"{path.name}:{i}:{chunk[:160]}"),
            "text": chunk,
            "tokens": tokenize(chunk),
            "metadata": {
                "source": path.name,
                "path": str(path),
                "chunk_index": i,
            },
        })
    return {"source": path.name, "chunks": len(chunks), "stored": bool(chunks)}


def score(query_tokens: list[str], doc_tokens: list[str]) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    q = Counter(query_tokens)
    d = Counter(doc_tokens)
    overlap = set(q) & set(d)
    if not overlap:
        return 0.0
    raw = sum(min(q[t], d[t]) for t in overlap)
    coverage = len(overlap) / max(1, len(set(query_tokens)))
    length_penalty = 1.0 / math.sqrt(max(1, len(doc_tokens) / 120))
    return round(raw * coverage * length_penalty, 6)


def search_knowledge(query: str, top_k: int = 5) -> list[dict]:
    q_tokens = tokenize(query)
    scored = []
    for row in read_chunks():
        s = score(q_tokens, row.get("tokens", []))
        if s > 0:
            scored.append({
                "text": row.get("text", ""),
                "metadata": row.get("metadata", {}),
                "score": s,
            })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:max(1, top_k)]


def format_context(hits: list[dict]) -> str:
    if not hits:
        return "NO_LOCAL_SOURCES_RETRIEVED"
    blocks = []
    for i, hit in enumerate(hits, start=1):
        meta = hit.get("metadata", {})
        blocks.append(
            f"[SOURCE {i}] {meta.get('source', 'unknown')} | chunk={meta.get('chunk_index', 'unknown')} | score={hit.get('score', 0)}\n{hit.get('text', '')}"
        )
    return "\n\n".join(blocks)
