from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json

from backend.config import settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def append_jsonl(path: str | Path, record: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def audit_event(event_type: str, payload: dict[str, Any]) -> None:
    append_jsonl(settings.audit_log_path, {"ts": utc_now(), "event_type": event_type, "payload": payload})


def source_ledger_event(payload: dict[str, Any]) -> None:
    append_jsonl(settings.source_ledger_path, {"ts": utc_now(), **payload})


def privacy_safe_prompt_payload(message: str) -> dict[str, Any]:
    payload = {
        "message_sha256": sha256_text(message),
        "message_length": len(message),
        "message_preview": message[:160],
    }
    if settings.log_full_prompts:
        payload["message_full"] = message
    return payload
