from backend.core.ingest import chunk_text
from backend.core.audit import sha256_text
from backend.core.rag import tokenize


def test_chunk_text_returns_chunks():
    chunks = chunk_text("A" * 2000, chunk_size=500, overlap=100)
    assert len(chunks) >= 4
    assert all(chunks)


def test_sha256_text_is_stable():
    assert sha256_text("ROSE") == sha256_text("ROSE")
    assert sha256_text("ROSE") != sha256_text("rose")


def test_tokenize_basic():
    assert "ucc" in tokenize("UCC Article 3")
