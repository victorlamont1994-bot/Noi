from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.core.audit import audit_event, privacy_safe_prompt_payload, sha256_bytes, source_ledger_event
from backend.core.llm import LLMError, ollama_chat
from backend.core.rag import format_context, ingest_file, search_knowledge
from backend.core.schemas import ChatRequest, ChatResponse, SearchHit, SearchRequest
from backend.core.security import require_rose_key


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_rose_prompt() -> str:
    return (Path(__file__).parent / "agents" / "rose_system.md").read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "model": settings.ollama_model,
        "api_key_required": settings.require_api_key,
        "strict_source_mode": settings.strict_source_mode,
        "index_path": settings.index_path,
    }


@app.post("/ingest", dependencies=[Depends(require_rose_key)])
async def ingest(file: UploadFile = File(...)):
    filename = Path(file.filename or "upload.bin").name
    target = Path(settings.upload_dir) / filename

    try:
        data = await file.read()
        max_bytes = settings.max_upload_mb * 1024 * 1024
        if len(data) > max_bytes:
            raise HTTPException(status_code=413, detail=f"Upload exceeds MAX_UPLOAD_MB={settings.max_upload_mb}.")

        file_hash = sha256_bytes(data)
        target.write_bytes(data)
        result = ingest_file(target)

        ledger_payload = {
            "source": filename,
            "path": str(target),
            "sha256": file_hash,
            "size_bytes": len(data),
            "chunks": result.get("chunks", 0),
            "content_type": file.content_type,
        }
        source_ledger_event(ledger_payload)
        audit_event("ingest", ledger_payload)

        return {**result, "sha256": file_hash, "size_bytes": len(data)}
    except HTTPException:
        raise
    except Exception as exc:
        audit_event("ingest_error", {"file": filename, "error": str(exc)})
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/search", dependencies=[Depends(require_rose_key)])
def search(req: SearchRequest):
    hits = search_knowledge(req.query, req.top_k)
    audit_event("search", {**privacy_safe_prompt_payload(req.query), "top_k": req.top_k, "hits": len(hits)})
    return {"query": req.query, "hits": hits}


@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(require_rose_key)])
def chat(req: ChatRequest):
    top_k = req.top_k or settings.default_top_k
    strict_sources = settings.strict_source_mode if req.strict_sources is None else req.strict_sources

    hits = search_knowledge(req.message, top_k=top_k)
    context = format_context(hits)

    audit_event(
        "chat_request",
        {**privacy_safe_prompt_payload(req.message), "top_k": top_k, "hits": len(hits), "strict_sources": strict_sources},
    )

    if strict_sources and context == "NO_LOCAL_SOURCES_RETRIEVED":
        answer = (
            "STRICT SOURCE MODE BLOCK: No local source material was retrieved. "
            "Upload authority, contracts, records, statutes, or filings first, then re-run the question."
        )
        audit_event("chat_blocked_strict_source", privacy_safe_prompt_payload(req.message))
        return ChatResponse(answer=answer, sources=[], model=settings.ollama_model)

    user_prompt = f"""
USER QUESTION:
{req.message}

LOCAL RETRIEVED CONTEXT:
{context}

INSTRUCTIONS:
- Use local retrieved context when relevant.
- If retrieved sources do not support the answer, say what is missing.
- Separate verified facts, assumptions, legal principles, and next actions.
- Do not invent case law, statutes, citations, account numbers, CUSIPs, or payment remedies.
- Strict source mode is: {strict_sources}.
"""

    try:
        answer = ollama_chat(system_prompt=load_rose_prompt(), user_prompt=user_prompt)
    except LLMError as exc:
        audit_event("chat_llm_error", {"error": str(exc)})
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    audit_event("chat_response", {"answer_length": len(answer), "source_count": len(hits), "model": settings.ollama_model})
    return ChatResponse(answer=answer, sources=[SearchHit(**hit) for hit in hits], model=settings.ollama_model)
